from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Room
from .forms import RoomForm, JoinRoomForm
from django.db.models import Q
from django.db import connection
from django.contrib.auth.forms import UserCreationForm

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            if not room.password:
                room.password = None
            room.save()
            room.participants.add(request.user)
            print(f"Room created: {room}")
            return redirect('room', room_id=room.id)
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = RoomForm()
    
    return render(request, 'create_room.html', {'form': form})

@login_required 
def join_room(request):
    if request.method == 'POST':
        form = JoinRoomForm(request.POST)
        if form.is_valid():
            room_id = form.cleaned_data['room_id']
            password = form.cleaned_data['password']
            
            try:
                # Fetch the room by ID
                room = Room.objects.get(id=room_id)
                print(f"Room found: {room.name}")  # Debug statement
                
                # Check if the password is required and correct
                if room.password and room.password != password:
                    print(f"Room password: {room.password}, Submitted Password; {password}")
                    form.add_error('password', 'Incorrect password')
                    return render(request, 'join_room.html', {'form': form, 'public_rooms': Room.objects.filter(password__isnull=True) | Room.objects.filter(password='')})
                
                # Add the user to the room's participants
                room.participants.add(request.user)
                print(f"User {request.user.username} added to room {room.name}")  # Debug statement
                print(f"Participants in room {room.name}: {room.participants.all()}")  # Debug statement
                return redirect('room', room_id=room.id)
                
            except Room.DoesNotExist:
                print("Room does not exist")  # Debug statement
                form.add_error('room_id', 'Room does not exist')
    else:
        form = JoinRoomForm()
    
    # Fetch public rooms (rooms with no password or empty password)
    public_rooms = Room.objects.all()
    print(f"Public rooms: {public_rooms}")  # Debug statement
    return render(request, 'join_room.html', {'form': form, 'public_rooms': public_rooms})

@login_required
def room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    # print(f"Participants in room {room.name}: {room.participants.all()}")  # Debug statement
    
    # Check if user is a participant
    if request.user not in room.participants.all():
        print(f"Access denied for user {request.user.username}")  # Debug statement
        return redirect('join_room')
    # print(f"Access granted for user {request.user.username}")  # Debug statement
    return render(request, 'room.html', {'room': room, 'room_id': room_id})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})