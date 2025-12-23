from django.views.generic import TemplateView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import login, authenticate

from engine.models import User, Gara, Soluzione, Squadra, Evento, Consegna, Jolly
from engine.forms import SignUpForm, RispostaFormset, SquadraFormset, InserimentoForm,\
    ModificaConsegnaForm, ModificaJollyForm, UploadGaraForm
from engine.formfields import IntegerMultiField

import json
import time
import logging
logger = logging.getLogger(__name__)


class CheckPermissionsMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin che controlla che l'utente sia autenticato e che soddisfi la funzione test_func.
    """
    pass


class IndexView(TemplateView):
    """ Pagina principale """
    template_name = "index.html"


class AboutView(TemplateView):
    """ Pagina 'chi siamo' """
    template_name = "about.html"


class SignUpView(FormView):
    """ Pagina di registrazione """
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = "/engine/"

    def form_valid(self, form):
        user = form.save()
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=user.username, password=raw_password)
        login(self.request, user)
        return super().form_valid(form)


class SignUpClosedView(TemplateView):
    """ Pagina per quando la registrazione è disabilitata """
    template_name = "registration/signup_closed.html"


#####################
#    VIEWS GARA     #
#####################

class CreaOModificaGaraView(SuccessMessageMixin):
    """ Superclasse per astrarre metodi comuni a CreaGaraView e ModificaGaraView"""
    model = Gara
    fields = ['nome', 'durata', 'durata_blocco', 'n_blocco', 'k_blocco',
              'num_problemi', 'cutoff', 'fixed_bonus', 'super_mega_bonus', 'jolly', 'testo']

    def get_form(self):
        form = super().get_form()
        # Cambia i campi per i bonus per avere caselle multiple
        form.fields['fixed_bonus'] = IntegerMultiField(
            required=False, require_all_fields=False,
            help_text=form.fields['fixed_bonus'].help_text,
            label=form.fields['fixed_bonus'].label,
            initial=form.fields['fixed_bonus'].initial)
        form.fields['super_mega_bonus'] = IntegerMultiField(
            required=False, require_all_fields=False,
            help_text=form.fields['super_mega_bonus'].help_text,
            label=form.fields['super_mega_bonus'].label,
            initial=form.fields['super_mega_bonus'].initial)
        return form

    def get_success_url(self, **kwargs):
        return reverse("engine:gara-admin", kwargs={'pk': self.object.pk})


class CreaGaraView(PermissionRequiredMixin, CreaOModificaGaraView, CreateView):
    """ View per la creazione di una gara """

    template_name = "gara/create.html"
    success_message = 'Gara creata con successo!'
    permission_required = "engine.add_gara"

    def form_valid(self, form):
        form.instance.admin = self.request.user
        response = super().form_valid(form)
        gara = form.instance
        for i in range(1, gara.num_problemi+1):
            Soluzione.objects.create(gara=gara, problema=i, nome="Problema {}".format(i))
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Errore: gara non creata correttamente")
        return super().form_invalid(form)


class GaraParametriView(CheckPermissionsMixin, CreaOModificaGaraView, UpdateView):
    """ View per cambiare i parametri di una gara """
    template_name = "gara/modify.html"
    success_message = 'Parametri di gara salvati con successo!'

    def test_func(self):
        # Salva la gara dentro self.object, così siamo sicuri
        # che sia stata validata e non viene chiamato get_object() due volte.
        self.object = self.get_object()
        return self.request.user.can_administrate(self.object)

    @transaction.atomic   # visto che creiamo nuovi problemi E aggiorniamo gara.num_problemi
    def form_valid(self, form):
        gara_nuova = form.instance
        gara_vecchia = self.get_object()

        if gara_nuova.num_problemi > gara_vecchia.num_problemi:
            # dobbiamo creare nuovi problemi
            for i in range(gara_vecchia.num_problemi+1, gara_nuova.num_problemi+1):
                Soluzione.objects.create(gara=gara_vecchia, problema=i, nome="Problema {}".format(i))
        elif gara_nuova.num_problemi < gara_vecchia.num_problemi:
            # dobbiamo cancellare problemi
            Soluzione.objects.filter(gara=gara_vecchia, problema__range=(gara_nuova.num_problemi+1, gara_vecchia.num_problemi)).delete()
        response = super().form_valid(form) # committa le modifiche
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Errore: parametri di gara non salvati correttamente")
        return super().form_invalid(form)


class GaraView(DetailView):
    """ View con riepilogo di una gara """
    model = Gara
    template_name = "gara/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["can_insert"] = self.request.user.can_insert_gara(self.object)
            context["is_admin"] = self.request.user.can_administrate(self.object)
        return context


class GaraAdminView(CheckPermissionsMixin, DetailView):
    """ View per l'amministrazione di una gara """
    model = Gara
    template_name = "gara/detail_admin.html"

    def test_func(self):
        # Salva la gara dentro self.object, così siamo sicuri
        # che sia stata validata e non viene chiamato get_object() due volte.
        self.object = self.get_object()
        return self.request.user.can_administrate(self.object)

    def post(self, request, *args, **kwargs):
        if "inizia" in request.POST:
            loraesatta = timezone.now()
            gara = self.object
            gara.inizio = loraesatta
            gara.save()
        return super().get(self, request)


class GaraRisposteView(CheckPermissionsMixin, SuccessMessageMixin, FormView, DetailView):
    """ View per l'inserimento delle soluzioni esatte di una gara """
    model = Gara
    template_name = 'gara/risposte.html'
    success_message = 'Soluzioni inserite con successo!'

    def test_func(self):
        self.object = self.get_object()
        return self.request.user.can_administrate(self.object)

    def get_success_url(self, **kwargs):
        return reverse("engine:gara-admin", kwargs={'pk': self.object.pk})

    def get_form(self):
        if self.request.POST:
            return RispostaFormset(self.request.POST)
        return RispostaFormset(queryset=Soluzione.objects.filter(gara=self.object))

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Errore: soluzioni non inserite correttamente")
        return super().form_invalid(form)


class GaraSquadreView(CheckPermissionsMixin, SuccessMessageMixin, FormView, DetailView):
    """ View per l'inserimento delle squadre partecipanti ad una gara """
    model = Gara
    template_name = 'gara/squadre.html'
    success_message = 'Squadre inserite con successo!'

    def test_func(self):
        self.object = self.get_object()
        return self.request.user.can_administrate(self.object)

    def get_success_url(self, **kwargs):
        return reverse("engine:gara-admin", kwargs={'pk': self.object.pk})

    def get_form(self):
        users = User.objects.all()
        if self.request.POST:
            return SquadraFormset(self.request.POST, users_qs=users)
        return SquadraFormset(queryset=self.object.squadre.all(), users_qs=users)

    def form_valid(self, form):
        for res in form.cleaned_data:
            sq = self.object.squadre.filter(num=res['num']).first()
            if sq:
                sq.nome = res['nome']
                sq.ospite = res['ospite']
                sq.consegnatore = res['consegnatore']
            else:
                sq = Squadra(gara=self.object, num=res['num'], nome=res['nome'], ospite=res['ospite'], consegnatore=res['consegnatore'])
            sq.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Errore: squadre non inserite correttamente")
        return super().form_invalid(form)


class UploadGaraView(PermissionRequiredMixin, SuccessMessageMixin, FormView):
    """ Importa una gara tramite l'upload di un file JSON """
    form_class = UploadGaraForm
    template_name = "gara/upload.html"
    success_message = "Gara caricata con successo!"
    permission_required = "engine.add_gara"

    def get_success_url(self):
        return reverse("engine:gara-detail", kwargs={'pk': self.gara.pk})

    def form_valid(self, form):
        gara_file = self.request.FILES['gara']
        gara_json = json.load(gara_file)
        self.gara = Gara.create_from_dict(gara_json)
        return super().form_valid(form)


class DownloadGaraView(DetailView):
    """ Serializza la gara e crea un json da scaricare """
    model = Gara

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        loraesatta = timezone.now()
        if self.object.get_ora_fine() >= loraesatta:
            return HttpResponse('Non puoi scaricare una gara in corso', status=404)
        data = self.object.dump_to_json()
        response = HttpResponse(data, content_type="application/json")
        response['Content-Disposition'] = 'attachment; filename={}.json'.format(self.object.nome)
        return response


#######################################
#             VIEW QUERY              #
#######################################

class QueryView(DetailView):
    """ Query: consente di cercare tra gli eventi """
    model = Gara
    template_name = 'gara/query.html'

    def test_func(self):
        self.object = self.get_object()
        return self.request.user.can_administrate(self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'eventi': self.object.get_all_eventi(self.request.user, self.request.GET.get('squadra'), self.request.GET.get('problema'), self.request.GET.get('risposta'))
        })
        return context


#######################################
#    VIEWS INSERIMENTO E MODIFICA     #
#######################################

class InserimentoView(CheckPermissionsMixin, DetailView, FormView):
    """ View per l'inserimento di una risposta durante la gara """
    model = Gara
    template_name = 'gara/inserimento.html'
    form_class = InserimentoForm

    def test_func(self):
        self.object = self.get_object()
        return self.request.user.can_insert_gara(self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'eventi': self.object.get_eventi(self.request.user)
        })
        return context

    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(InserimentoView, self).get_form_kwargs()
        kwargs['gara'] = self.object
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse("engine:inserimento", kwargs={'pk': self.get_object().pk})

    def form_valid(self, form, *args, **kwargs):
        consegna = form.get_instance()
        consegna.creatore = self.request.user
        res = consegna.maybe_save()
        if res[0]:
            messages.info(self.request, res[1])
        else:
            messages.warning(self.request, res[1])
        return super().form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request, "Inserimento non riuscito")
        return super().form_invalid(form)


class ModificaEventoView(CheckPermissionsMixin, DetailView, FormView):
    model = Evento
    template_name = "forms/evento_modifica.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(creatore=self.request.user)

    def test_func(self):
        self.object = self.get_object()
        return self.request.user.can_edit_or_delete(self.object)

    def get_form_class(self):
        if self.object.subclass == "Consegna":
            return ModificaConsegnaForm
        elif self.object.subclass == "Jolly":
            return ModificaJollyForm

    def get_initial(self):
        c = self.object.as_child()
        if self.object.subclass == "Consegna":
            initial = {'problema': c.problema, 'risposta': c.risposta}
        elif self.object.subclass == "Jolly":
            initial = {'jolly': c.problema}
        return initial

    def get_success_url(self, **kwargs):
        return reverse("engine:inserimento", kwargs={'pk': self.get_object().gara.pk})

    def form_valid(self, form):
        self.object = self.object.as_child()
        if self.object.subclass == "Consegna":
            self.object.problema = form.cleaned_data.get('problema')
            self.object.risposta = form.cleaned_data.get('risposta')
            self.object.maybe_save()
        elif self.object.subclass == "Jolly":
            self.object.problema = form.cleaned_data.get('jolly')
            self.object.maybe_save()
        return super().form_valid(form)


class EliminaEventoView(CheckPermissionsMixin, DeleteView):
    model = Evento

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(creatore=self.request.user)

    def test_func(self):
        self.object = self.get_object()
        return self.request.user.can_edit_or_delete(self.object)

    def get_success_url(self):
        return reverse('engine:inserimento', kwargs={'pk': self.object.gara.pk})


####################################
#    VIEWS STATO E CLASSIFICA     #
###################################

class StatusView(DetailView):
    model = Gara

    def get(self, request, *args, **kwargs):
        gara = self.get_object()
        resp = {}
        resp['last_update'] = gara.get_last_update()

        if "last_event" in request.GET:
            resp['consegne'] = gara.get_consegne(request.GET["last_event"])
            resp['jolly'] = gara.get_jolly(request.GET["last_event"])
            return JsonResponse(resp)

        resp['nome'] = gara.nome
        resp['inizio'] = gara.inizio
        resp['squadre'] = gara.get_squadre()
        resp['n_prob'] = gara.num_problemi
        resp['problemi'] = gara.get_problemi()
        resp['fixed_bonus'] = gara.fixed_bonus_array
        resp['super_mega_bonus'] = gara.super_mega_bonus_array
        resp['n_blocco'] = gara.n_blocco
        resp['k_blocco'] = gara.k_blocco
        resp['cutoff'] = gara.cutoff
        resp['jolly_enabled'] = gara.jolly
        if request.user.is_authenticated:
            ids = list(gara.squadre.filter(consegnatore=request.user).values_list("num", flat=True).all())
        else:
            ids = []
        resp['consegnatore_per'] = ids

        if gara.inizio is None:
            return JsonResponse(resp)

        resp['fine'] = gara.get_ora_fine()
        resp['tempo_blocco'] = gara.get_ora_blocco()

        resp['consegne'] = gara.get_consegne()
        resp['jolly'] = gara.get_jolly()

        return JsonResponse(resp)


class ClassificaView(DetailView):
    """ Visualizzazione classifica """
    model = Gara
    template_name = "classifiche/squadre.html"


class PuntiProblemiView(DetailView):
    """ Visualizzazione punteggi problemi """
    model = Gara
    template_name = "classifiche/punti_problemi.html"

    def get_context_data(self, **kwargs):
        context = super(PuntiProblemiView, self).get_context_data(**kwargs)
        context['soluzioni'] = self.object.soluzioni.all().order_by("problema")
        return context


class StatoProblemiView(DetailView):
    """ Visualizzazione stato problemi: quali sono stati risolti e quali no """
    model = Gara
    template_name = "classifiche/stato_problemi.html"

    def get_context_data(self, **kwargs):
        context = super(StatoProblemiView, self).get_context_data(**kwargs)
        context['soluzioni'] = self.object.soluzioni.all().order_by("problema")
        return context


class CronacaView(DetailView):
    """ Visualizzazione stato problemi: quali sono stati risolti e quali no """
    model = Gara
    template_name = "classifiche/cronaca.html"


class UnicaView(DetailView):
    """ Visualizzazione unica: tutte le informazioni """
    model = Gara
    template_name = "classifiche/unica.html"

    def get_context_data(self, **kwargs):
        context = super(UnicaView, self).get_context_data(**kwargs)
        context['soluzioni'] = self.object.soluzioni.all().order_by("problema")
        return context
