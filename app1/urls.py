from django.db import router
from rest_framework.routers import DefaultRouter
from app1 import views
from django.urls import path


router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet, basename='task'),
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'tasksearch', views.TaskSearchView, basename='task-search')

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('tasks/<int:pk>/mark-completed/',views.TaskViewSet.as_view({'post': 'mark_task_completed'}), name='mark-task-completed'),
    path('tasks/<int:pk>/mark-incomplete/', views.TaskViewSet.as_view({'post': 'mark_task_incomplete'}), name='mark-task-incomplete'),

]+ router.urls