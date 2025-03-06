from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from authentication.views import UserViewSet, RegisterView, CustomLoginView
from projectsmanagement.views import ProjectViewSet, CommentViewSet, IssueViewSet


router = routers.SimpleRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"issues", IssueViewSet, basename="issues")
router.register(r"comments", CommentViewSet, basename="comments")


urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"api-auth/", include("rest_framework.urls")),
    path(r"api-auth/login/", CustomLoginView.as_view(), name="api-login"),
    path(r"token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(r"token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(r"register/", RegisterView.as_view(), name="auth_register"),
    path(r"api/", include(router.urls)),
]
