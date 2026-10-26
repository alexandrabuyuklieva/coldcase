from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from common.mixins import FilteredListMixin
from .forms import AlibiForm, SuspectFilterForm, SuspectForm
from .models import Alibi, Suspect


class SuspectListView(FilteredListMixin, ListView):
    queryset = Suspect.objects.with_suspicion()
    filter_form_class = SuspectFilterForm
    template_name = 'suspects/suspect_list.html'
    context_object_name = 'suspects'
    paginate_by = 8

    def filter_queryset(self, queryset, filters):
        query = filters['q']
        case = filters['case']
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(alias__icontains=query)
            )
        if case:
            queryset = queryset.filter(cases=case)
        return queryset


class SuspectDetailView(DetailView):
    template_name = 'suspects/suspect_detail.html'
    context_object_name = 'suspect'

    def get_queryset(self):
        return Suspect.objects.with_suspicion()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alibis'] = self.object.alibis.all()
        context['cases'] = self.object.cases.all()
        context['evidence_list'] = self.object.implicating_evidence.select_related('case')
        return context


class SuspectCreateView(SuccessMessageMixin, CreateView):
    model = Suspect
    form_class = SuspectForm
    template_name = 'suspects/suspect_form.html'
    success_message = '%(first_name)s %(last_name)s е добавен към заподозрените.'

    def get_initial(self):
        initial = super().get_initial()
        case_pk = self.request.GET.get('case')
        if case_pk and case_pk.isdigit():
            initial['cases'] = [case_pk]
        return initial


class SuspectUpdateView(SuccessMessageMixin, UpdateView):
    model = Suspect
    form_class = SuspectForm
    template_name = 'suspects/suspect_form.html'
    success_message = 'Промените по заподозрения са запазени.'


class SuspectDeleteView(SuccessMessageMixin, DeleteView):
    model = Suspect
    template_name = 'suspects/suspect_confirm_delete.html'
    success_url = reverse_lazy('suspects:list')
    success_message = 'Заподозреният е изтрит.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alibis_count = self.object.alibis.count()
        evidence_count = self.object.implicating_evidence.count()
        warnings = []
        if alibis_count:
            warnings.append(f'Ще бъдат изтрити и {alibis_count} алибита.')
        if evidence_count:
            warnings.append(f'{evidence_count} улики вече няма да сочат към никого.')
        context['warning'] = ' '.join(warnings)
        return context


class AlibiCreateView(SuccessMessageMixin, CreateView):
    model = Alibi
    form_class = AlibiForm
    template_name = 'suspects/alibi_form.html'
    success_message = 'Алибито е записано.'

    def dispatch(self, request, *args, **kwargs):
        self.suspect = get_object_or_404(Suspect, pk=kwargs['suspect_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = Alibi(suspect=self.suspect)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suspect'] = self.suspect
        return context


class AlibiUpdateView(SuccessMessageMixin, UpdateView):
    model = Alibi
    form_class = AlibiForm
    template_name = 'suspects/alibi_form.html'
    success_message = 'Алибито е обновено.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suspect'] = self.object.suspect
        return context


class AlibiDeleteView(SuccessMessageMixin, DeleteView):
    model = Alibi
    template_name = 'suspects/alibi_confirm_delete.html'
    success_message = 'Алибито е изтрито.'

    def get_success_url(self):
        return self.object.suspect.get_absolute_url()
