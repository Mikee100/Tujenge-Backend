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
from .views import MonthlyProgressView
from .views import LoanListCreateView
from .views import AllLoansView
from .views import LoanUpdateView

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
    path('chama/<int:chama_id>/progress/', MonthlyProgressView.as_view(), name='monthly-progress'),
]

urlpatterns += [
    path('loans/', LoanListCreateView.as_view(), name='loans-list-create'),
    path('loans/all/', AllLoansView.as_view(), name='all-loans'),
    path('loans/<int:pk>/update/', LoanUpdateView.as_view(), name='loan-update'),
]