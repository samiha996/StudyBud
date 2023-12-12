from django.shortcuts import render, redirect
from .models import Room,Message,Topic,User
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required


from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
# Create your views here.

def login_page(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method=='POST':
        email=request.POST.get('email').lower()
        password=request.POST.get('password')
        
        try:
            user=User.objects.get(email=email)
        except:
            messages.error(request, 'User does not Exist!')
        
        user=authenticate(request,email=email,password=password)
        
        if user is not  None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Wrong Username or Password!')

    context={'page':page}
    return render(request,'base/login_register.html',context)


def logout_user(request):
    logout(request)
    return redirect('home')

def register_user(request):
    form=MyUserCreationForm
    if request.method=='POST':
        form=MyUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'The passwrod is weak or similar to your username!')
    context={'form':form}
    return render(request,'base/login_register.html',context)

    

def home(request):
    q=request.GET.get('q') if request.GET.get('q') !=None else ''
    rooms=Room.objects.filter(Q(topic__name__icontains=q) | 
                              Q(name__icontains=q) | 
                              Q(description__icontains=q))
    
    rooms_count=rooms.count()
    topics=Topic.objects.all()[0:5]
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    context={'rooms':rooms,'topics':topics, 'rooms_count':rooms_count,'room_messages':room_messages}
    return render(request, 'base/home.html',context=context)

def room(request,pk):
    room=Room.objects.get(id=pk)
    comments=room.message_set.all().order_by('-created')
    participants=room.participants.all()

    if request.method=='POST':
        comment=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    
    context={'room':room, 'comments':comments,'participants': participants}
    return render(request,'base/room.html',context=context)


def user_profile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,'rooms':rooms,'topics':topics,'room_messages':room_messages}
    return render(request,'base/user_profile.html',context)


@login_required(login_url='login')
def create_room(request):
    form=RoomForm
    topics=Topic.objects.all()
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic, created=Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    # if request.method=='POST':
    #     # print(request.POST)
    #     form=RoomForm(request.POST)
    #     if form.is_valid():
    #         room=form.save(commit=False)
    #         room.host=request.user
    #         room.save()
            
            
    context={'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def update_room(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    topics=Topic.objects.all()
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic, created=Topic.objects.get_or_create(name=topic_name)
        room.topic=topic
        room.name=request.POST.get('name')
        room.description=request.POST.get('description')
        room.save()
        return redirect('home')
        # form=RoomForm(request.POST,instance=room)
        # if form.is_valid():
        #     form.save()
        
    context={'form':form,'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)


@login_required(login_url='login')
def delete_room(request,pk):
    room=Room.objects.get(id=pk)
    
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete_confirm.html',{'obj':room})

@login_required(login_url='login')
def delete_message(request,pk):
    message=Message.objects.get(id=pk)
    room=message.room
    if request.method=='POST':
        message.delete()
        return redirect('room',room.id)
        
    return render(request,'base/delete_confirm.html',{'obj':message})



def update_user(request):
    user=request.user
    form=UserForm(instance=user)
    
    if request.method=='POST':
        form=UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid:
            form.save(commit=False)
            user.username=user.username.lower()
            form.save()
        return redirect('user-profile',user.id)
            
    
    context={'form':form}
    return render(request,'base/update-user.html',context)


def topic_page(request):
    q=request.GET.get('q') if request.GET.get('q')!=None else ''
    topics=Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics':topics})

def activity_page(request):
    room_messages=Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})