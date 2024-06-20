from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


# Отслеживаем переходы
urlpatterns = [
                  path('', index, name='home'),
                  path('guide', guide, name='guide'),
                  path('TZ', TZ_F, name='TZ'),
                  path('check_username/', CheckUsernameView.as_view(), name='check_username'),
                  path('result', result, name='result'),
                  path('rating', rating, name='rating'),
                  path('guide_detail/<int:pk>', guide_detail, name='guide_detail'),
                  path('tz_detail/<int:pk>', tz_detail, name='tz_detail'),

                  path('new_block', new_block, name='new_block'),
                  path('blok/<int:pk>', block, name='block'),

                  path('new_guide', new_guide, name='new_guide'),
                  path('new_tz', new_tz, name='new_tz'),

                  path('vopros/<int:N>/<int:ind>/', create_question, name='new_vopros'),

                  path('test/<int:pk>', test, name='test'),

                  path('block/<int:guide_id>/delete/', delete_block, name='delete_block'),
                  path('test/<int:pk>/delete/', DELIT, name='delete_test'),

                  path('guides/<int:guide_id>/delete/', delete_guide, name='delete_guide'),

                  path('delete_tz/<int:pk>/', delete_tz, name='delete_tz'),

                  path('edit_guide/<int:pk>/', edit_guide, name='edit_guide'),
                  path('tz_answer/<int:pk>/', answer_tz, name='tz_answer'),

                  path('result/<str:correct_answers>/<str:alls>/<str:ind>/', save_result, name='result'),

                  path("new_test/<int:ind>/", new_question, name="new_test"),
                  path('register', RegisterFormView.as_view(), name='register'),
                  path('login', LoginUser.as_view(), name='login'),
                  path('logout', LogoutUser, name='logout'),
                  path('Infor', Infor, name='Infor'),
                  path("look_tz/<int:pk>/", look_tz, name='look_tz'),
                  path('polls/', poll_list, name='poll_list'),
                  path('polls/<int:pk>/', poll_detail, name='poll_detail'),
                  path('polls/<int:pk>/submit/', submit_poll, name='submit_poll'),
                  path('polls/create/',create_poll, name='create_poll'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
