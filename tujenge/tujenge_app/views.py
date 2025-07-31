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

from django.db.models import Sum
from .models import Contribution

class MonthlyProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chama_id):
        # Get all contributions for the user in this chama
        contributions = Contribution.objects.filter(
            chama_id=chama_id,
            user=request.user
        ).values('month').annotate(
            total_amount=Sum('amount')
        ).order_by('-month')

        # Calculate progress for each month
        monthly_progress = []
        target = 2000

        for contrib in contributions:
            month = contrib['month']
            total_amount = float(contrib['total_amount'])
            progress_percent = min(100, (total_amount / target) * 100)
            
            monthly_progress.append({
                'month': month,
                'contributed': total_amount,
                'target': target,
                'progress_percent': round(progress_percent, 1),
                'is_complete': total_amount >= target
            })

        return Response({
            'monthly_progress': monthly_progress,
            'target': target
        })


from .models import Loan
from .serializers import LoanSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

class LoanListCreateView(generics.ListCreateAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user).order_by('-requested_date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, chama=self.request.user.chama)

class AllLoansView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show loans for the user's chama
        return Loan.objects.filter(chama=self.request.user.chama).order_by('-requested_date')

class LoanUpdateView(generics.UpdateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if serializer.instance.status == 'pending' and self.request.data.get('status') in ['approved', 'rejected']:
            serializer.save(
                approved_date=timezone.now(),
                approved_by=self.request.user
            )
        else:
            serializer.save()