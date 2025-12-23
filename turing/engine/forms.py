from django import forms
from engine.models import User
from django.core.validators import FileExtensionValidator
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from crispy_forms.helper import FormHelper

from engine.models import Squadra, Soluzione, Jolly, Consegna
from dateutil.parser import parse
from mathrace_interaction.journal_reader import journal_reader
from mathrace_interaction.filter.strip_mathrace_only_attributes_from_imported_turing import (
    strip_mathrace_only_attributes_from_imported_turing)

import io
import json

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class RispostaEsattaFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(RispostaEsattaFormSet, self).__init__(*args, **kwargs)
        no_of_forms = len(self)
        for i in range(0, no_of_forms):
            self[i].fields['risposta'].label += " {}".format(i + 1)
            self[i].fields['problema'].widget = forms.HiddenInput()


RispostaFormset = forms.modelformset_factory(
    Soluzione, fields=('problema', 'risposta', 'nome', 'punteggio'),
    extra=0, formset=RispostaEsattaFormSet,)


class BaseSquadraFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        users_qs = kwargs.pop("users_qs")
        super().__init__(*args, **kwargs)
        users_qs.all = lambda: users_qs
        users_qs.iterator = users_qs.all

        # Apply the common (non-cloning) querysets to all the forms
        for form in self.forms:
            form.fields["consegnatore"].queryset = users_qs

    def clean(self, *args, **kwargs):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        squadre = []
        ids = []
        for form in self.forms:
            id = form.cleaned_data["num"]
            sq = form.cleaned_data['nome']
            if sq in squadre:
                raise forms.ValidationError('I nomi delle squadre devono essere distinti!')
            if id in ids:
                raise forms.ValidationError('Gli identificativi delle squadre devono essere unici!')
            squadre.append(sq)
            ids.append(id)


class SquadraForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'forms/inline_field.html'

    class Meta:
        model = Squadra
        fields = ['num', 'nome', 'ospite', 'consegnatore']


SquadraFormset = forms.modelformset_factory(
                    Squadra, form=SquadraForm,
                    extra=0, formset=BaseSquadraFormSet,)


class SquadraChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_id_nome()


class InserimentoForm(forms.Form):
    problema = forms.IntegerField(min_value=1)
    risposta = forms.IntegerField(min_value=0, max_value=9999, required=False)
    jolly = forms.BooleanField(required=False)
    squadra = SquadraChoiceField(required=True, queryset=None)

    def __init__(self, *args, **kwargs):
        self.gara = kwargs.pop('gara', None)
        self.user = kwargs.pop('user', None)
        super(InserimentoForm, self).__init__(*args, **kwargs)
        if self.gara:
            self.fields['squadra'].queryset = self.gara.get_squadre_inseribili(self.user)
            self.fields['squadra'].empty_label = None
            self.fields['squadra'].widget.attrs.update({'autofocus': ''})

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        if bool(cleaned_data['jolly']) != bool(cleaned_data['risposta'] is None):
            raise forms.ValidationError('Inserire la risposta o il jolly, ma non entrambi')

        if bool(cleaned_data['jolly']) and Jolly.objects.filter(squadra = cleaned_data['squadra']).exists():
            raise forms.ValidationError('Ė già stato inserito un jolly per la squadra')

        obj = self.get_instance()
        obj.clean()
        return cleaned_data

    def get_instance(self):
        if self.cleaned_data.get('jolly'):
            return Jolly(gara=self.gara, squadra=self.cleaned_data.get('squadra'),
                         problema=self.cleaned_data.get('problema'))
        else:
            return Consegna(gara=self.gara, squadra=self.cleaned_data.get('squadra'),
                            problema=self.cleaned_data.get('problema'),
                            risposta=self.cleaned_data.get('risposta'))


class ModificaConsegnaForm(forms.Form):
    problema = forms.IntegerField(min_value=1, max_value=50)
    risposta = forms.IntegerField(min_value=0, max_value=9999)


class ModificaJollyForm(forms.Form):
    jolly = forms.IntegerField(min_value=1, max_value=50)


class UploadGaraForm(forms.Form):
    gara = forms.FileField(
        label="Gara", help_text="Scegli il file .journal o .json contente la gara da importare",
        validators=[FileExtensionValidator(allowed_extensions=["journal", "json"])])
    eventi_futuri = forms.BooleanField(
        required=False, initial=False, label="Consenti eventi futuri", help_text=(
            "Spuntare per consentire eventi che hanno data nel futuro. Di default tali eventi non sono consentiti, "
            "perché possono creare confusione tra gli inseritori i quali, guardando la classifica, "
            "vedrebbero comparire gradualmente eventi senza che loro li stiano inserendo"
        ))
    eventi_riordina = forms.BooleanField(
        required=False, initial=False, label="Riordina automaticamente eventi", help_text=(
            "Spuntare per riordinare automaticamente gli eventi in ordine cronologico crescente. "
            "Caricare un file con eventi disordinati può creare problemi nella visualizzazione della classifica, "
            "perché gli inserimento non arrivano in ordine corretto. Di default gli eventi non vengono automaticamente "
            "riordinati ma, se questa opzione non è selezionata, viene comunque controllato che siano già nell'ordine "
            "cronologico corretto"
        ))
    nome_gara = forms.CharField(
        label="Nome della gara (richiesto solo per il formato .journal)",
        initial="Disfida", required=False)
    data_gara = forms.DateTimeField(
        label="Data della gara (richiesto solo per il formato .journal)",
        initial=timezone.now(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        gara_file = cleaned_data["gara"]
        if gara_file.name.endswith(".json"):
            gara_json = json.load(gara_file)
        elif gara_file.name.endswith(".journal"):
            race_name = cleaned_data["nome_gara"]
            race_date = cleaned_data["data_gara"]
            with journal_reader(io.TextIOWrapper(gara_file, encoding="utf-8")) as journal_stream:
                # Disable strict processing: incorrectly sorted events will be handled according to
                # the choice in eventi_riordina
                journal_stream.strict_timestamp_race_events = False
                try:
                    gara_json = journal_stream.read(race_name, race_date)
                except RuntimeError as e:
                    raise forms.ValidationError(f"Errore nella conversione del file journal: {e}")
            strip_mathrace_only_attributes_from_imported_turing(gara_json)

        has_inizio = ("inizio" in gara_json and gara_json["inizio"] is not None)
        has_eventi = ("eventi" in gara_json)
        if not has_inizio and has_eventi:
            raise forms.ValidationError(f'La gara contiene eventi ma non ha una data di inizio')

        if has_eventi:
            if cleaned_data["eventi_riordina"]:
                gara_json['eventi'] = list(sorted(gara_json['eventi'], key=lambda e: (
                    e["orario"], e["subclass"], e["squadra_id"], e["problema"] if "problema" in e else None)))

            loraesatta = timezone.now()
            orario_precedente = parse(gara_json["inizio"])
            for evento in gara_json["eventi"]:
                orario = parse(evento["orario"])
                if not cleaned_data["eventi_futuri"] and orario > loraesatta:
                    raise forms.ValidationError(f'La gara contiene eventi che hanno data nel futuro, ad esempio in data {evento["orario"]}')
                if orario < orario_precedente:
                    raise forms.ValidationError(f"La gara contiene eventi in ordine non cronologico crescente, ad esempio l'evento alle {orario_precedente} viene prima dell'evento delle {orario}")
                else:
                    orario_precedente = orario

        cleaned_data["gara_json"] = gara_json
        return cleaned_data
