from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from cases.models import Case
from common.mixins import FilteredListMixin
from .forms import EvidenceEditForm, EvidenceFilterForm, EvidenceForm
from .models import Evidence


class EvidenceListView(FilteredListMixin, ListView):
    queryset = Evidence.objects.select_related('case', 'implicates')
    filter_form_class = EvidenceFilterForm
    template_name = 'evidence/evidence_list.html'
    context_object_name = 'evidence_list'
    paginate_by = 10

    def filter_queryset(self, queryset, filters):
        query = filters['q']
        evidence_type = filters['evidence_type']
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(found_at__icontains=query)
                | Q(description__icontains=query)
            )
        if evidence_type:
            queryset = queryset.filter(evidence_type=evidence_type)
        return queryset


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_cases'] = Case.objects.exists()
        return context


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
