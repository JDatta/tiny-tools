Robo News
================
A command line news headline reader written in Python.

It uses Google News to get the current news headlines. Default invocation displays topics
as given in the res directory: urls.txt (file containing a list of newsfeed URIs) and 
topics.txt (a file containing the order of the topic to display)

This program can also be used to search for ANY arbitrary news topic. Following is one example
invocation:

```
[joydip@localhost src]$ ./robonews.py search "tamilnadu"
Getting your feeds. Please wait...



==========================================
  Tamilnadu HEADLINES (7225.08 ms)
==========================================
 1: Tamil Nadu loses 800MW of wind power to poor transmission - Times of India
 2: Top Engineering Colleges in Tamil Nadu- Ratings 2013 - Oneindia
 3: In Tamil Nadu, Politics Meets Idlis - New York Times (blog)
 4: Power sector still an irritant in Tamil Nadu - Hindustan Times
 5: Tamil Nadu government transfers six senior IAS officials - Times of India
 6: Tamilnadu To Hasten Monorail Project - Bernama
 7: TamilNadu Board Class 12th results 2013 declared: Check result here - Newstrack India
 8: Tamil Nadu SSLC/ Class 10 Results expected on 4th of June - Oneindia
 9: TamilNadu HSC Results 2013 to be declared on 9th May - Newstrack India
10: LTTE commemorations in Tamilnadu banned - Hiru News
```

