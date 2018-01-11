# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

from django.http import HttpResponse


from .models import Todo


def index(request):
	todos = Todo.objects.all()[:10]
	context = {
	'name': 'Suraj',

	'Todos': todos
	}
	return render(request, 'index.html',context)

def details(request, id):
	todos = Todo.objects.get(id= id)
	context = {
	'Todos': todos
	}
	return render(request, 'details.html',context)


def add(request):

	if(request.method == 'POST'):

		title = request.POST['title']
		text = request.POST['text']

		todo = Todo(title = title, text = text)
		todo.save()

		return redirect('/todos')
	else:
		return render(request, 'add.html')


