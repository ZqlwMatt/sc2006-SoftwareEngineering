import re
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import OuterRef, Subquery, Q
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, UpdateView, TemplateView
from django_tables2 import tables, SingleTableView, Column, A, RequestConfig

from main.forms import (
    ReportIncidentForm,
    RegisterForm,
    UserSettingsForm,
    NotificationPreferenceForm,
    VerifyReportForm,
)
from main.models import (
    NotificationPreference,
    Incident,
    IncidentReport,
    MajorDisruption, Announcement, Congestion
)
from sc2006_project.utils import GroupConcat


class CreateUpdateView(UpdateView):

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except AttributeError:
            return None

def get_stn_num(x):
    num = ''.join(re.findall(r'\d+', x['Station']))
    if num.isnumeric(): return int(num)
    return 0

class MainManager(TemplateView):
    template_name = "MainUI.html"

    @classmethod
    def is_lta_user(cls, request):
        return request.user.groups.filter(name="lta_users").exists()

    @classmethod
    def get_lta_crowd_level(cls, request, train_line):
        data = Congestion.query_db_json().get(train_line, {})
        data['value'] = sorted(
            data.get("value", []),
            key=get_stn_num
        )
        if "error" in data:
            return JsonResponse({}, safe=False)
        else:
            return JsonResponse(data, safe=False)
    def dispatch(self, request, *args, **kwargs):
        if self.is_lta_user(request):
            return ViewReportManager.as_view()(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

class LoginManager(View):
    template_name = "registration/LoginInterface.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/")

        return render(request, self.template_name)

    def post(self, request):
        next_url = request.GET.get("next", "/")

        if request.user.is_authenticated:
            return redirect(next_url)

        user = authenticate(
            username=request.POST["username"],
            password=request.POST["password"],
        )

        if user is not None:
            login(request, user)
            return redirect(next_url)

        message = "Incorrect username or password. Please try again."
        return render(request, self.template_name, context={"message": message})


class LogoutHandler(View):
    def get(self, request):
        logout(request)
        return redirect("/")


class RegisterManager(CreateView):
    template_name = "registration/RegisterInterface.html"
    form_class = RegisterForm
    model = get_user_model()

    def get_success_url(self):
        return reverse("main:login") + "?sign_up=1"

class MajorDisruptionTable(tables.Table):
    affected_stations = Column(accessor=A("affected_station_names"))
    class Meta:
        exclude = ("id", "resolved_at")
        attrs = {"class": "table"}
        model = MajorDisruption
        orderable = False

class IncidentTableUser(tables.Table):
    details = Column(accessor=A("announcement"))
    class Meta:
        exclude = ("resolved_at", "resolved_by", "escalated_at", "id")
        attrs = {"class": "table"}
        model = Incident

class CurrentDisruptionManager(SingleTableView):
    template_name = "CurrentDisruptionInterface.html"
    table_class = MajorDisruptionTable

    def get_queryset(self):
        qset = (
            MajorDisruption.objects
            .prefetch_related("affected_stations")
            .filter(resolved_at__isnull=True)
            .annotate(affected_station_names=GroupConcat("affected_stations__station__name"))
        )
        return qset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        newest = Announcement.objects.filter(id=OuterRef("id")).order_by("-added_at")
        context['table_incidents'] = IncidentTableUser(
            Incident.objects
                .prefetch_related("announcements")
                .filter(resolved_at__isnull=True)
                .annotate(announcement=Subquery(newest.values("content")[:1])),
            orderable=False
        )
        return context


class ReportIncidentManager(CreateView):
    template_name = "forms/ReportIncidentInterface.html"
    form_class = ReportIncidentForm
    success_url = "/"

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)
        form.fields['station'].initial = self.request.GET.get("station")
        return form

    def check_and_escalate(self, incident_report):
        """
        Checks whether the number of reports has reached the threshold.
        Creates an Incident if threshold is met.
        :param IncidentReport incident_report: The incident report being created.
        """
        time_from = timezone.now() - timedelta(hours=Incident.TIME_THRESHOLD)

        previous_incident_reports = IncidentReport.objects.filter(
            ~Q(reported_by_id=incident_report.reported_by.id),
            reported_at__gte=time_from,
            station_id=incident_report.station.id,
        )

        previous_incidents = Incident.objects.filter(
            station_id=incident_report.station.id,
            started_at__gte=time_from
        )

        if len(previous_incident_reports) >= (Incident.REPORTS_THRESHOLD - 1):
            incident = Incident.objects.create(
                started_at=previous_incident_reports.earliest("reported_at").reported_at,
                station_id=incident_report.station.id
            )
            previous_incident_reports.update(incident=incident)
            incident_report.incident = incident

        elif previous_incidents.exists():
            previous_incident = previous_incidents.latest("started_at")
            previous_incident.incident_reports.add(incident_report)

        incident_report.save()

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.reported_by = self.request.user
        obj.save()
        self.object = obj
        self.check_and_escalate(obj)
        return HttpResponseRedirect(self.get_success_url())

class UserSettingsManager(UpdateView):
    template_name = "forms/UserSettingsInterface.html"
    form_class = UserSettingsForm
    model = get_user_model()

    @classmethod
    def delete_preference(cls, request, pk=None):
        try:
            pref = NotificationPreference.objects.get(id=pk)
        except NotificationPreference.DoesNotExist:
            return redirect("main:user_preferences")

        if request.user.id != pref.user.id:
            return redirect("main:user_preferences")

        pref.delete()
        return redirect("main:user_preferences")

    def get_context_data(self, **kwargs):
        extra_context = {"preferences": self.get_object().preferences.all()}
        return super().get_context_data() | extra_context

    def get_object(self, **kwargs):
        return get_user_model().objects.get(pk=self.request.user.id)

    def get_success_url(self):
        return reverse("main:user_preferences")


class AddPreferenceManager(CreateUpdateView):
    template_name = "forms/AddPreferenceInterface.html"
    form_class = NotificationPreferenceForm
    model = NotificationPreference

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)
        form.fields['stations'].initial = [self.request.GET.get("station")]
        return form

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object and self.object.user.pk != self.request.user.pk:
            raise Http404()
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("main:user_preferences")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        self.object = obj
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())

class IncidentTable(tables.Table):
    manage = Column(accessor=A("manage_button"), verbose_name="")
    status = Column(accessor=A("status"), verbose_name="Status")
    station = Column(accessor=A("station"))

    class Meta:
        exclude = ("resolved_at", "resolved_by")
        sequence = ("id", "station", "started_at", "escalated_at", "status", "manage")
        model = Incident
        attrs = {"class": "table"}

class IncidentReportTable(tables.Table):
    class Meta:
        exclude = ("incident", "id", "station")
        model = IncidentReport
        attrs = {"class": "table"}

class LTAPermissionMixin(View):
    def check_permissions_lta(self, request=None):
        return (request or self.request).user.groups.filter(name="lta_users").exists()

class ViewReportManager(SingleTableView, LTAPermissionMixin):
    template_name = "lta/ViewReportInterface.html"
    model = Incident
    table_class = IncidentTable
    def get(self, request, *args, **kwargs):
        if not self.check_permissions_lta(request):
            raise Http404()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("incident_reports")
        if self.request.GET.get("show_resolved"):
            return qs
        return qs.filter(resolved_at__isnull=True)


class VerifyReportManager(LTAPermissionMixin):
    template_name = "lta/VerifyReportInterface.html"
    form_class = VerifyReportForm
    model = Incident

    def get_success_url(self):
        return reverse("main:view_reports")

    def get(self, *args, **kwargs):
        if not self.check_permissions_lta(self.request):
            raise Http404()

        has_announcements = False
        incident = self.model.objects.get(pk=kwargs["pk"])
        form = self.form_class()

        if self.request.GET.get("resolve") == "1":
            incident.resolved_by_id = self.request.user.id
            incident.resolved_at = timezone.now()
            incident.save()
            return redirect("main:view_reports")

        table = IncidentReportTable(IncidentReport.objects.filter(incident_id=incident.pk))
        RequestConfig(self.request).configure(table)

        if incident.announcements.exists():
            has_announcements = True
            form = self.form_class(instance=incident.announcements.first())

        return render(self.request, self.template_name, {
            "form": form, "table": table, "station": incident.station, "id": incident.pk,
            "has_announcements": has_announcements
        })

    def post(self, *args, **kwargs):
        if not self.check_permissions_lta(self.request):
            raise Http404()

        incident = self.model.objects.get(pk=kwargs["pk"])

        instance = None
        if incident.announcements.exists():
            instance = incident.announcements.first()

        form = self.form_class(self.request.POST, instance=instance) # update existing if there is one

        announcement = form.save(commit=False)
        announcement.added_by = self.request.user
        announcement.incident = self.model.objects.get(pk=kwargs["pk"])
        announcement.save()

        return HttpResponseRedirect(self.get_success_url())
