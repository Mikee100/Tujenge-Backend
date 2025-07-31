from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from .models import User, Chama
from django.utils.crypto import get_random_string
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .serializers import OTPVerificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import generics
from .serializers import RoleUpdateSerializer
from rest_framework.permissions import BasePermission
from .serializers import ChamaMemberSerializer
from .models import Contribution
from .serializers import ContributionSerializer
from rest_framework import serializers
from rest_framework import  permissions
from .models import Loan
from .serializers import LoanSerializer
from django.db.models import Sum , Count
from datetime import datetime
from collections import defaultdict
from .serializers import VaultSummarySerializer, VaultGrowthSerializer,VaultPieSerializer, VaultActivitySerializer
from django.utils.timezone import now
import calendar

# Create your views here.
class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = get_random_string(length=6, allowed_chars='0123456789')
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
 
            return Response({"message": "User created. OTP sent to email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_verified = True
            
            user.otp = None  
            user.otp_created_at = None
            user.save()
            return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class RoleUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = RoleUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

class RoleBasedDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'admin':
            return Response({"message": "Welcome Admin!"})
        elif request.user.role == 'treasurer':
            return Response({"message": "Welcome Treasurer!"})
        elif request.user.role == 'member':
            return Response({"message": "Welcome Member!"})
        else:
            return Response({"error": "Unauthorized"}, status=403)

class ChamaMembersView(APIView):
    def get(self, request, chama_id):
        try:
            chama = Chama.objects.get(id=chama_id)
        except Chama.DoesNotExist:
            return Response({'error': 'Chama not found'}, status=status.HTTP_404_NOT_FOUND)
        members = chama.members.all()
        serializer = ChamaMemberSerializer(members, many=True)
        return Response(serializer.data)

class ContributionListCreateView(generics.ListCreateAPIView):
    serializer_class = ContributionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chama_id = self.kwargs['chama_id']
        return Contribution.objects.filter(chama_id=chama_id).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        

class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = ['id', 'amount', 'month', 'chama', 'user', 'date']
        read_only_fields = ['user', 'date']        

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # You can customize the fields returned as needed
        return Response({
            "id": str(user.id),
            "email": user.email,
            "chama": user.chama.id if user.chama else None,
            "role": user.role,
        })        

class MyContributionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chama_id):
        contributions = Contribution.objects.filter(chama_id=chama_id, user=request.user).order_by('-date')
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)        

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import ChamaMemberSerializer  # or create a new UserSerializer

class AllMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = ChamaMemberSerializer(users, many=True)
        return Response(serializer.data)        

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Contribution
from .serializers import ContributionSerializer

class AllContributionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contributions = Contribution.objects.select_related('user').all().order_by('-date')
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)        

class LoanView(APIView):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, chama_id):
        loans = Loan.objects.filter(user=request.user, chama_id=chama_id).order_by('-date_requested')
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, chama_id):
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, chama_id=chama_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VaultStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        chama = user.chama

        if not chama:
            return Response({"error": "User is not part of any Chama."}, status=400)

        contributions = Contribution.objects.filter(chama=chama)

        total_contributions = contributions.aggregate(total=Sum('amount'))['total'] or 0

        growth_data = defaultdict(float)
        for c in contributions:
            growth_data[c.month] += float(c.amount)

        growth_chart = [{"month": month, "amount": amount} for month, amount in growth_data.items()]

   
        pie_data = [
            {"label": "Contributions", "value": float(total_contributions)},

        ]

        recent = contributions.order_by('-date')[:5]
        recent_list = [
            {
                "user": c.user.email,
                "amount": float(c.amount),
                "date": c.date.strftime('%Y-%m-%d'),
                "month": c.month
            } for c in recent
        ]

        return Response({
            "totalVaultBalance": total_contributions,
            "totalContributions": total_contributions,
            "vaultGrowthChart": growth_chart,
            "vaultDistributionChart": pie_data,
            "recentVaultActivity": recent_list
        })
    
class VaultSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        chama = user.chama
        total_contributions = Contribution.objects.filter(chama=chama).aggregate(total=Sum("amount"))["total"] or 0
        total_loans_disbursed = Loan.objects.filter(chama=chama, status="approved").aggregate(total=Sum("amount"))["total"] or 0
        total_repayments = Loan.objects.filter(chama=chama, status="repaid").aggregate(total=Sum("amount"))["total"] or 0
        total_balance = total_contributions + total_repayments - total_loans_disbursed
        total_members = User.objects.filter(chama=chama).count()

        data = {
            "total_balance": total_balance,
            "total_contributions": total_contributions,
            "total_members": total_members,
        }

        serializer = VaultSummarySerializer(data)
        return Response(serializer.data)


class VaultGrowthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        chama = user.chama

        contributions = Contribution.objects.filter(chama=chama)
        month_totals = defaultdict(float)

        for c in contributions:
            month = c.date.strftime("%B")
            month_totals[month] += float(c.amount)

    
        month_order = list(calendar.month_name)[1:]  # Jan to Dec
        result = [{"month": month, "balance": month_totals.get(month, 0)} for month in month_order if month_totals.get(month)]

        serializer = VaultGrowthSerializer(result, many=True)
        return Response(serializer.data)


class VaultPieView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        chama = user.chama

        contributions = Contribution.objects.filter(chama=chama).aggregate(total=Sum("amount"))["total"] or 0
        loans = Loan.objects.filter(chama=chama, status="approved").aggregate(total=Sum("amount"))["total"] or 0
        repayments = Loan.objects.filter(chama=chama, status="repaid").aggregate(total=Sum("amount"))["total"] or 0

        data = {
            "contributions": contributions,
            "loans": loans,
            "repayments": repayments
        }

        serializer = VaultPieSerializer(data)
        return Response(serializer.data)


class VaultActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        chama = user.chama

        contributions = Contribution.objects.filter(chama=chama).order_by("-date")[:5]
        loans = Loan.objects.filter(chama=chama).order_by("-date_requested")[:5]

        activity_list = []

        for c in contributions:
            activity_list.append({
                "type": "Contribution",
                "user": c.user.email,
                "amount": c.amount,
                "date": c.date
            })

        for l in loans:
            if l.status == "repaid":
                activity_type = "Repayment"
            elif l.status == "approved":
                activity_type = "Loan Disbursed"
            else:
                continue

            activity_list.append({
                "type": activity_type,
                "user": l.user.email,
                "amount": l.amount,
                "date": l.date_requested.date()
            })

        activity_list = sorted(activity_list, key=lambda x: x["date"], reverse=True)[:10]

        serializer = VaultActivitySerializer(activity_list, many=True)
        return Response(serializer.data)

