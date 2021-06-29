import random


def main():
    print(random.random())
    print(random.randrange(9000, 10000))
    print(random.randint(9000, 10000))
    items = ["Hello", 3, "Potato", "Cake"]
    print(random.choice(items))
    random.shuffle(items)
    print(items)
    u = random.uniform(200, 500)
    print(u)
    if random.random() > 0.5:
        print("50/50")

    names = ['Kitchen', 'Animal', 'State', 'Tasty', 'Big', 'City', 'Fish', 'Pizza', 'Goat', 'Salty', 'Sandwich',
             'Lazy', 'Fun']
    company_type = ['LLC', 'Inc', 'Company', 'Corporation']
    company_cuisine = ['Pizza', 'Bar Food', 'Fast Food', 'Italian', 'Mexican', 'American', 'Sushi Bar', 'Vegetarian']
    for x in range(1, 501):
        business = {
            'name': names[random.randint(0, (len(names) - 1))] + ' ' + names[
                random.randint(0, (len(names) - 1))] + ' ' + company_type[random.randint(0, (len(company_type) - 1))],
            'rating': random.randint(1, 5),
            'cuisine': company_cuisine[random.randint(0, (len(company_cuisine) - 1))]
        }
        print(business)


if __name__ == '__main__':
    main()
