import json
from django import forms
from .models import ShortUrl, UserUrl
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_safe, require_POST, require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


class UrlForm(forms.Form):
    url = forms.URLField(max_length=255)
    path = forms.CharField(required=False, max_length=255)
    note = forms.CharField(required=False, max_length=255)


class AccountForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(max_length=255)


# 73 characters, 62 alpha-numeric
convertor = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$-_.+!*'(),"


def encode(num):
    if (num >= len(convertor)):
        res = encode(num // len(convertor))
    else:
        res = ''

    res += convertor[num % len(convertor)]
    return res


@require_http_methods(['GET', 'POST', 'HEAD'])
def index(request):
    if request.method == 'POST':
        res = json.loads(urls(request).content)
        return render(request, 'index.html', {'res': res})

    # GET or HEAD
    return render(request, 'index.html')


@require_safe
def u(request, path):
    res = json.loads(url(request, path).content)

    if res['url']:
        if res['note']:
            return render(request, 'note.html', {'res': res})

        return redirect(res['url'])
    raise Http404


@require_safe
def url(request, path):
    try:
        res = ShortUrl.objects.get(path=path)
    except ShortUrl.DoesNotExist:
        return JsonResponse({'url': False})

    res.viewed += 1
    res.save()

    return JsonResponse({
        'url': res.url,
        'note': res.note
    })


@require_POST
def urls(request):
    form = UrlForm(request.POST)
    if form.is_valid():
        num = ShortUrl.objects.latest().id if ShortUrl.objects.exists() else 0
        path = form.cleaned_data['path']

        if path:
            if ShortUrl.objects.filter(path=path):
                return JsonResponse({
                    'message': 'This url is already taken',
                    'url': False
                })
        else:
            path = encode(num)
            while ShortUrl.objects.filter(path=path):
                num += 1
                path = encode(num)

        path = ShortUrl.objects.create(
            id=num + 1,
            path=path,
            url=form.cleaned_data['url'],
            note=form.cleaned_data['note']
        )

        if request.user.is_authenticated:
            UserUrl.objects.create(user=request.user, url=path)

        return JsonResponse({
            'message': f'{request.scheme}://{request.get_host()}/u/{path.path}',
            'url': True
        })

    return JsonResponse({
        'message': json.dumps(form.errors)[1:-1],  # Removes the "{}"
        'url': False
    })


@require_http_methods(['GET', 'POST', 'DELETE', 'HEAD'])
@login_required
def link(request, path):
    try:
        path = ShortUrl.objects.get(
            path=path,
            userurl__user=request.user
        )
    except ShortUrl.DoesNotExist:
        return JsonResponse({'url': False})

    if request.method == 'POST':
        form = UrlForm(request.POST)

        if form.is_valid():
            if path.path != form.cleaned_data['path'] and ShortUrl.objects.filter(path=form.cleaned_data['path']):
                return JsonResponse({
                    'message': 'This url is already taken'
                })

            for field in ['url', 'path', 'note']:
                setattr(path, field, form.cleaned_data[field])

            path.save()
            return redirect(reverse('links'))

    if request.method == 'DELETE':
        path.delete()
        return JsonResponse({'url': False})

    # GET or HEAD
    return render(request, 'link/link.html', {'path': path})


@require_safe
@login_required
def links(request):
    urls = ShortUrl.objects.filter(userurl__user=request.user)
    return render(request, 'link/links.html', {'urls': urls})


@require_POST
def register(request):
    form = AccountForm(request.POST)
    if form.is_valid():
        if User.objects.filter(username=form.cleaned_data['username']):
            return JsonResponse({
                    'message': 'This username is already taken'
                })

        params = {
            'username': form.cleaned_data['username'],
            'password': form.cleaned_data['password']
        }

        if User.objects.exists():
            User.objects.create_user(**params)
        else:
            User.objects.create_superuser(**params)

    return redirect(reverse('login'))
