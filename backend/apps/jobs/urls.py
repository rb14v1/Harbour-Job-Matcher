from rest_framework.routers import DefaultRouter

from apps.jobs.views import JobPostingViewSet

router = DefaultRouter()
router.register(r"", JobPostingViewSet, basename="jobposting")

urlpatterns = router.urls
