from django.db.models import Count, Q
from django.views.generic import TemplateView

from cases.models import Case
from evidence.models import Evidence
from suspects.models import Suspect


class HomeView(TemplateView):
    template_name = 'common/home.html'
    latest_cases_count = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case_stats'] = Case.objects.aggregate(
            total=Count('pk'),
            open=Count('pk', filter=Q(status=Case.Status.OPEN)),
            solved=Count('pk', filter=Q(status=Case.Status.SOLVED)),
            frozen=Count('pk', filter=Q(status=Case.Status.FROZEN)),
        )
        context['suspects_count'] = Suspect.objects.count()
        context['evidence_count'] = Evidence.objects.count()
        context['latest_open_cases'] = (
            Case.objects
            .filter(status=Case.Status.OPEN)
            .annotate(evidence_count=Count('evidence', distinct=True))
            .order_by('-created_at')
            [:self.latest_cases_count]
        )
        return context
