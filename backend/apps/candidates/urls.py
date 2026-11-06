from rest_framework.routers import DefaultRouter

from apps.candidates.views import CandidateViewSet

router = DefaultRouter()
router.register(r"", CandidateViewSet, basename="candidate")

urlpatterns = router.urls
