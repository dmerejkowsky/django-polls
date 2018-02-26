from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.views import generic


from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.filter(
            pub_date__lte=timezone.now()
            ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    try:
        choice_id = request.POST['choice']
        selected_choice = question.choice_set.get(pk=choice_id)
    except KeyError:
        context['error_message'] = "Missing 'choice' param in form data"
        return render(request, 'polls/detail.html', context)
    except Choice.DoesNotExist:
        context['error_message'] = "Invalid choice"
        return render(request, 'polls/detail.html', context)
    else:
        print('choice_id', choice_id)
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
