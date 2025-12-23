from django import forms
from engine.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper

from engine.models import Squadra, Soluzione, Jolly, Consegna

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
    gara = forms.FileField(label="Gara", help_text="Scegli il file JSON contente la gara da importare")
