from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Skill, Message
from django.contrib.auth.models import User


from.forms import CustormUserCreationForm, ProfileForm, SkillForm, MessageForm

# Create your views here.


def loginUser(request):

    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == "POST":
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.object.get(username=username)
        except:
            messages.error(request, 'username Does Not Exist !!')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request, 'User Name or password is incorrect')
    context = {'page': 'Login'}
    return render(request, 'users/login_register.html', context)


def logoutUser(req):
    logout(req)
    messages.info(req, 'user Was logged out')
    return redirect('login')


def registerUser(request):

    form = CustormUserCreationForm()

    if request.method == "POST":
        form = CustormUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User Accout was created!!!')
            login(request, user)
            return redirect('edit-account')
        else:
            messages.error(
                request, 'AN error has occured during registration!!!')

    context = {'page': 'register', 'form': form}
    return render(request, 'users/login_register.html', context)


def profiles(request):

    search_query = ''
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    skills = Skill.objects.filter(name__icontains=search_query)

    profiles = Profile.objects.distinct().filter(
        Q(name__icontains=search_query) |
        Q(short_intro__icontains=search_query) |
        Q(skill__in=skills)
    )
    context = {'profiles': profiles, 'search_query': search_query}
    return render(request, 'users/profiles.html', context)


def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)

    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")

    context = {'profile': profile, 'topSkills': topSkills,
               'otherSkills': otherSkills}
    return render(request, 'users/user-profile.html', context)


@login_required(login_url='login')
def userAccount(request):

    profile = request.user.profile
    skills = profile.skill_set.all()
    projects = profile.project_set.all()

    context = {'profile': profile, 'skills': skills, 'projects': projects}
    return render(request, 'users/account.html', context)


# @login_required(login_url='login')
# def editAccount(request):
#     profile = request.user.profile
#     form = ProfileForm(instance=profile)

#     if request.method == 'POST':
#         form = ProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()

#             return redirect('account')

#     context = {'form': form}
#     return render(request, 'users/profile_form.html', context)


@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form = SkillForm()

    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Skill Added successfully !! ')
            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


# @login_required(login_url='login')
# def updateSkill(request, pk):
#     profile = request.user.profile
#     skill = profile.skill_set.get(id=pk)
#     form = SkillForm(instance=skill)

#     if request.method == "POST":
#         form = SkillForm(request.POST, instance=skill)
#         if form.is_valid():
#             form.save()

#             messages.info(request, 'Skill Updated successfully !! ')
#             return redirect('account')

#     context = {'form': form}
#     return render(request, 'users/skill_form.html', context)


# @login_required(login_url='login')
# def deleteSkill(request, pk):
#     profile = request.user.profile
#     skill = profile.skill_set.get(id=pk)

#     if request.method == "POST":
#         skill.delete()
#         messages.info(request, 'Skill Deleted successfully !! ')
#         return redirect('account')
#     context = {'object': skill}
#     return render(request, 'delete_template.html', context)


@login_required(login_url='login')
def inbox(request):

    profile = request.user.profile
    msg = profile.messages.all()
    unreadCount = msg.filter(is_read=False).count()
    context = {'messageRequests': msg, 'unreadCount': unreadCount}
    return render(request, 'users/inbox.html', context)


@login_required(login_url='login')
def viewMessage(request, pk):
    profile = request.user.profile
    msg = profile.messages.get(id=pk)
    if msg.is_read == False:
        msg.is_read = True
        msg.save()
    context = {'message': msg}
    return render(request, 'users/message.html', context)


def createMessage(request, pk):
    recipient = Profile.objects.get(id=pk)
    # profile = request.user.profile
    form = MessageForm()

    try:
        sender = request.user.profile

    except:
        sender = None

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = sender
            msg.recipient = recipient

            if sender:
                msg.name = sender.name
                msg.email = sender.email
            msg.save()

            messages.success(request, 'your msg is successfully send!!!')
            return redirect('user-profile', pk=recipient.id)

    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/message_form.html', context)
