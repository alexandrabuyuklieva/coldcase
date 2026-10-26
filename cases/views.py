from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from common.mixins import FilteredListMixin
from .forms import CaseFilterForm, CaseForm
from .models import Case


class CaseListView(FilteredListMixin, ListView):
    queryset = Case.objects.annotate(
        evidence_count=Count('evidence', distinct=True),
        suspects_count=Count('suspects', distinct=True),
    )
    filter_form_class = CaseFilterForm
    template_name = 'cases/case_list.html'
    context_object_name = 'cases'
    paginate_by = 6

    def filter_queryset(self, queryset, filters):
        query = filters['q']
        status = filters['status']
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(case_number__icontains=query)
                | Q(location__icontains=query)
                | Q(victim__icontains=query)
            )
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['filter_form']
        context['current_status'] = form.cleaned_data.get('status', '') if form.is_valid() else ''
        context['status_choices'] = Case.Status.choices
        return context


class CaseDetailView(DetailView):
    model = Case
    template_name = 'cases/case_detail.html'
    context_object_name = 'case'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evidence_list'] = self.object.evidence.select_related('implicates')
        context['suspects'] = self.object.suspects.with_suspicion()
        return context


class CaseCreateView(SuccessMessageMixin, CreateView):
    model = Case
    form_class = CaseForm
    template_name = 'cases/case_form.html'
    success_message = 'Досие %(case_number)s е открито.'

    def get_success_message(self, cleaned_data):
        return self.success_message % {'case_number': self.object.case_number}


class CaseUpdateView(SuccessMessageMixin, UpdateView):
    model = Case
    form_class = CaseForm
    template_name = 'cases/case_form.html'
    success_message = 'Промените по досието са запазени.'


class CaseDeleteView(SuccessMessageMixin, DeleteView):
    model = Case
    template_name = 'cases/case_confirm_delete.html'
    success_url = reverse_lazy('cases:list')
    success_message = 'Досието е унищожено.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evidence_count = self.object.evidence.count()
        if evidence_count:
            context['warning'] = f'Заедно с досието ще бъдат изтрити и {evidence_count} улики.'
        return context
