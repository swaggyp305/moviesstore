from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required


def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def stats(request):
    
    movies = Movie.objects.all()
    mostReview = -1
    mostOrdered = -1
    
    for movie in movies:
        if mostReview == -1:
            mostReview = movie
        elif mostReview.review_num < movie.review_num:
            mostReview = movie
            
        if mostOrdered == -1:
            mostOrdered = movie
        elif mostOrdered.orders_num < movie.orders_num:
            mostOrdered = movie
    
    template_data = {}
    template_data['title'] = 'Statistics'
    template_data['mostReviewed'] = mostReview
    template_data['mostOrdered'] = mostOrdered
    return render(request, 'movies/stats.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    rated_reviews = reviews.filter(rating__isnull=False)

    if rated_reviews.exists():
        avg = sum(r.rating for r in rated_reviews) / rated_reviews.count()
        average_rating = round(avg, 1)
    else:
        average_rating = None

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['average_rating'] = average_rating
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        
        movie.review_num += 1
        movie.save()

        rating_val = request.POST.get('rating')
        if rating_val:
            review.rating = int(rating_val)

        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']

        rating_val = request.POST.get('rating')
        if rating_val:
            review.rating = int(rating_val)
        else:
            review.rating = None

        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    movie = review.movie
    movie.review_num -= 1
    movie.save()
    
    review.delete()

    return redirect('movies.show', id=id)

def get_most_user_and_comment():
    reviews = Review.objects.all()
    count = {}
    for review in reviews:
        theuser = review.user
        if theuser in count.keys():
            count[theuser] = count.get(theuser) + 1
        else:
            count[theuser] = 1
    
    most_user = None
    most_count = 0

    for theuser, thecount in count.items():
        if thecount > most_count:
            most_user = theuser
            most_count = thecount
    
    return most_user, most_count