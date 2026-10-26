from django import forms


class StyledFormMixin:
    placeholders = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                css_class = 'choice-list'
            elif isinstance(widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-input'
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing} {css_class}'.strip()

        for name, placeholder in self.placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs['placeholder'] = placeholder


class DisabledFieldsMixin:
    disabled_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.disabled_fields:
            if name in self.fields:
                self.fields[name].disabled = True
                self.fields[name].help_text = 'Това поле не може да се променя.'


class SortableFilterForm(StyledFormMixin, forms.Form):
    SORT_CHOICES = ()
    SORT_ORDERING = {}
    DEFAULT_SORT = None

    sort = forms.ChoiceField(
        required=False,
        label='Подреждане',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sort'].choices = self.SORT_CHOICES
        self.order_fields([name for name in self.fields if name != 'sort'] + ['sort'])

    def ordering(self):
        sort = self.cleaned_data.get('sort') if self.is_valid() else None
        return self.SORT_ORDERING[sort or self.DEFAULT_SORT]
