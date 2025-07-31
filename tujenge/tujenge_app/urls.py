from django.urls import path
from .views import SignupView

from rest_framework_simplejwt.views import TokenRefreshView
from .views import VerifyOTPView
from .views import RoleUpdateView
from .views import RoleBasedDashboard
from .views import CustomTokenObtainPairView
from .views import ChamaMembersView
from .views import ContributionListCreateView
from .views import UserProfileView
from .views import MyContributionsView
from .views import AllMembersView
from .views import AllContributionsView
from .views import LoanView
from .views import VaultStatsView
from .views import VaultSummaryView, VaultGrowthView, VaultPieView, VaultActivityView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('users/<int:pk>/update-role/', RoleUpdateView.as_view(), name='update-role'),
    path('dashboard/', RoleBasedDashboard.as_view(), name='role-dashboard'), 
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('chama/members/<int:chama_id>/', ChamaMembersView.as_view(), name='chama-members'),
    path('chama/<int:chama_id>/contributions/', ContributionListCreateView.as_view(), name='contributions-list-create'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('vaults-stats/', VaultStatsView.as_view(), name='vault-stats'),
     
]

urlpatterns += [
    path('chama/<int:chama_id>/my-contributions/', MyContributionsView.as_view(), name='my-contributions'),
]

urlpatterns += [
    path('members/all/', AllMembersView.as_view(), name='all-members'),
]

urlpatterns += [
    path('contributions/all/', AllContributionsView.as_view(), name='all-contributions'),
]

urlpatterns += [
    path('chama/<int:chama_id>/loans/', LoanView.as_view(), name='loan-list-create'),
]
urlpatterns += [
    path('summary/', VaultSummaryView.as_view()),
    path('growth/', VaultGrowthView.as_view()),
    path('pie/', VaultPieView.as_view()),
    path('activity/', VaultActivityView.as_view()),
]



    
