class FilteredListMixin:
    filter_form_class = None

    def get_filter_form(self):
        if not hasattr(self, '_filter_form'):
            self._filter_form = self.filter_form_class(self.request.GET or None)
        return self._filter_form

    def filter_queryset(self, queryset, filters):
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_filter_form()
        if form.is_valid():
            queryset = self.filter_queryset(queryset, form.cleaned_data)
        return queryset.order_by(*form.ordering())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.get_filter_form()
        return context
