from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from cases.models import Case
from .forms import EvidenceEditForm, EvidenceFilterForm, EvidenceForm
from .models import Evidence


class EvidenceListView(ListView):
    model = Evidence
    template_name = 'evidence/evidence_list.html'
    context_object_name = 'evidence_list'
    paginate_by = 10

    def get_filter_form(self):
        if not hasattr(self, '_filter_form'):
            self._filter_form = EvidenceFilterForm(self.request.GET or None)
        return self._filter_form

    def get_queryset(self):
        queryset = super().get_queryset().select_related('case', 'implicates')
        form = self.get_filter_form()
        if form.is_valid():
            query = form.cleaned_data['q']
            evidence_type = form.cleaned_data['evidence_type']
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query)
                    | Q(found_at__icontains=query)
                    | Q(description__icontains=query)
                )
            if evidence_type:
                queryset = queryset.filter(evidence_type=evidence_type)
        return queryset.order_by(*form.ordering())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.get_filter_form()
        return context


class EvidenceDetailView(DetailView):
    model = Evidence
    template_name = 'evidence/evidence_detail.html'
    context_object_name = 'evidence'

    def get_queryset(self):
        return super().get_queryset().select_related('case', 'implicates')


class EvidenceCreateView(SuccessMessageMixin, CreateView):
    model = Evidence
    form_class = EvidenceForm
    template_name = 'evidence/evidence_form.html'
    success_message = 'Уликата „%(title)s“ е добавена към досието.'

    def get_initial(self):
        initial = super().get_initial()
        case_pk = self.request.GET.get('case')
        if case_pk and case_pk.isdigit():
            initial['case'] = Case.objects.filter(pk=case_pk).first()
        return initial


class EvidenceUpdateView(SuccessMessageMixin, UpdateView):
    model = Evidence
    form_class = EvidenceEditForm
    template_name = 'evidence/evidence_form.html'
    success_message = 'Промените по уликата са запазени.'


class EvidenceDeleteView(SuccessMessageMixin, DeleteView):
    model = Evidence
    template_name = 'evidence/evidence_confirm_delete.html'
    success_message = 'Уликата е унищожена.'

    def get_success_url(self):
        return self.object.case.get_absolute_url()
