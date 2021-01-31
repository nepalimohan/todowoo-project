from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "todo/home.html")


def loginuser(request):
    if request.method == 'GET':
        return render(request, "todo/loginuser.html", {'form': AuthenticationForm()})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['username'])
        if user is None:
            return render(request, "todo/loginuser.html", {'form': AuthenticationForm(), 'error': 'Username and password donot match'})
        login(request, user)
        return redirect('currenttodos')


def signupuser(request):
    if request.method == 'GET':
        return render(request, "todo/signupuser.html", {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, "todo/signupuser.html", {'form': UserCreationForm(), 'error': 'Please pick another username. User exists'})

        else:
            return render(request, "todo/signupuser.html", {'form': UserCreationForm(), 'error': 'Passwords did not match.'})


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, "todo/currenttodos.html", {'todos': todos})


@login_required
def completedtodos(request):
    todos = Todo.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')  # '-' does the most recent completed todo at top
    return render(request, "todo/completedtodos.html", {'todos': todos})


@login_required
def viewtodo(request, todo_pk):
    # user here authenticates so that todo of another user is not accessed
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)  # fills out the info stored in DB
        return render(request, "todo/viewtodo.html", {'todo': todo, 'form': form})
    else:
        try:
            # instance here used to identify its not new data to DB
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, "todo/viewtodo.html", {'todo': todo, 'form': form, 'error': 'Bad information fed'})


@login_required
def createtodo(request):
    if request.method == 'GET':
        # django seprate form is custom made in forms.py
        return render(request, "todo/createtodo.html", {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            # does not yet save to the database
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, "todo/createtodos.html", {'form': TodoForm(), 'error': 'Please choose a short title.'})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()  # to delete you just have to use todo.delete()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datedeleted = timezone.now()
        if todo.datedeleted is False:
            todo.datedeleted = True
        # to delete you just have to use todo.delete()
        todo.delete()
        return redirect('currenttodos')
