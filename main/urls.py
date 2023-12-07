from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = "main"

class MainManager():
    urlpatterns = [
        path("login/", views.LoginManager.as_view(), name="login"),
        path("logout/", views.LogoutHandler.as_view(), name="logout"),
        path("sign-up/", views.RegisterManager.as_view(), name="sign_up"),
        path(
            "disruptions/",
            views.CurrentDisruptionManager.as_view(),
            name="current_disruptions",
        ),
        path(
            "user-settings/",
            login_required(views.UserSettingsManager.as_view()),
            name="user_preferences",
        ),
        path(
            "forms/report-incident/",
            login_required(views.ReportIncidentManager.as_view()),
            name="report_incident",
        ),
        path(
            "forms/add-preference/",
            login_required(views.AddPreferenceManager.as_view()),
            name="add_preference",
        ),
        path(
            "forms/add-preference/<int:pk>/",
            login_required(views.AddPreferenceManager.as_view()),
            name="update_preference",
        ),
        path(
            "forms/delete-preference/<int:pk>/",
            login_required(views.UserSettingsManager.delete_preference),
            name="delete_preference",
        ),
        path(
            "lta/manage-reports/",
            login_required(views.ViewReportManager.as_view()),
            name="view_reports",
        ),
        path(
            "lta/manage-reports/<int:pk>/",
            login_required(views.VerifyReportManager.as_view()),
            name="verify_reports",
        ),
        path('viewmaps/apicall/<str:train_line>/', views.MainManager.get_lta_crowd_level, name='lta_crowd_level'),
    ]

urlpatterns = MainManager.urlpatterns