from django.contrib import messages
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit
from django.contrib.postgres.search import SearchQuery, SearchRank

from .forms import SubmissionForm, VictimFilterForm
from .models import Tag, Victim


@require_GET
def home(request):
    recent = Victim.objects.prefetch_related("photos").order_by("-created_at")[:6]
    verified_count = Victim.objects.filter(
        verification_status=Victim.VerificationStatus.VERIFIED
    ).count()
    context = {
        "recent": recent,
        "verified_count": verified_count,
    }
    return render(request, "victims/home.html", context)


@cache_page(60)
def victim_list(request):
    form = VictimFilterForm(request.GET)
    victims = Victim.objects.all().prefetch_related("tags", "photos")
    if form.is_valid():
        q = form.cleaned_data.get("q")
        city = form.cleaned_data.get("city")
        verification_status = form.cleaned_data.get("verification_status")
        age_min = form.cleaned_data.get("age_min")
        age_max = form.cleaned_data.get("age_max")
        tag = form.cleaned_data.get("tag")
        sort = form.cleaned_data.get("sort")

        if q:
            if connection.vendor == "postgresql":
                search_query = SearchQuery(q)
                victims = victims.filter(search_vector=search_query).annotate(
                    rank=SearchRank(F("search_vector"), search_query)
                )
                victims = victims.order_by("-rank")
            else:
                victims = victims.filter(
                    Q(full_name__icontains=q)
                    | Q(native_name__icontains=q)
                    | Q(biography__icontains=q)
                )
        if city:
            victims = victims.filter(city_of_death__icontains=city)
        if verification_status:
            victims = victims.filter(verification_status=verification_status)
        if age_min is not None:
            victims = victims.filter(age__gte=age_min)
        if age_max is not None:
            victims = victims.filter(age__lte=age_max)
        if tag:
            victims = victims.filter(tags__slug=tag)

        if sort == "alpha":
            victims = victims.order_by("full_name")
        elif sort == "age":
            victims = victims.order_by("age")
        elif sort == "date":
            victims = victims.order_by("-date_of_death")
        else:
            victims = victims.order_by("-created_at")

    paginator = Paginator(victims, 12)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    tags = Tag.objects.all()

    context = {
        "form": form,
        "page_obj": page_obj,
        "tags": tags,
    }
    return render(request, "victims/victim_list.html", context)


@require_GET
def victim_detail(request, slug):
    victim = get_object_or_404(
        Victim.objects.prefetch_related("photos", "sources", "tags"), slug=slug
    )
    return render(request, "victims/victim_detail.html", {"victim": victim})


@require_GET
def disclaimer(request):
    return render(request, "victims/disclaimer.html")


@ratelimit(key="ip", rate="5/h", block=True)
def submit_correction(request, slug=None):
    initial = {}
    if slug:
        victim = get_object_or_404(Victim, slug=slug)
        initial = {"victim": victim}
    if request.method == "POST":
        form = SubmissionForm(request.POST, initial=initial)
        if form.is_valid():
            submission = form.save(commit=False)
            if slug:
                submission.victim = victim
            submission.save()
            messages.success(
                request, "Thank you. Your submission has been received for review."
            )
            return redirect("victim_list")
    else:
        form = SubmissionForm(initial=initial)
    return render(request, "victims/submit_correction.html", {"form": form})


@require_GET
def name_suggest(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})
    results = (
        Victim.objects.filter(full_name__icontains=query)
        .values_list("full_name", flat=True)[:8]
    )
    return JsonResponse({"results": list(results)})
