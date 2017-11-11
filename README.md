
![alt text](logo.png)

# PyAmplitude

...What is Pyamplitude ?

Amplitude its a python-based client designed to interact with the entire set of Amplitude Analytics services (Redshift, Export API, Dashboard Rest API and Behavioral Cohorts API) following the official Amplitude Documentation which can be found at:  

https://amplitude.zendesk.com/hc/en-us/categories/115000290488-Technical-Resources

General Organization:

     AmplitudeRestApi   -> A wrapper around each Rest API resources.
     RedshfitAmplitude  -> A sql connector for the Amplitude AWS-Redshift database.
     ExportApi          -> A wrapper around the entire Amplitude export

Aditional Modules:

    Resources      -> Api resources ( Manage several apps & secret keys, import Segments to get data using Segment definitions )

Aditional Features:

    - Calculate each query cost.
    - Manage your query rate limits in a ETL context.
    - Visualize the quentity of requests and your query limit status.

## Install

sudo pip install pyamplitude

## How to use PyAmplitude ?

Let's start by importing the ProjectHandler and passing a project_name, api_key and api_secret key as parameters.


```python
from pyamplitude.projectshandler import ProjectsHandler
```

Lets instance the ProjectHanlder with our first app called 'BubbleWay'...


```python
bubbleConector = ProjectsHandler(project_name = 'BubbleWay',
                                 api_key      = <'API-KEY'>,
                                 api_secret   = <'API-SECRET'>)
```

Hint: Use the __repr__ method to check your actual instance when used with several apps.


```python
print bubbleConector
```

project_name: BubbleWay | api_key: API-KEY | secret_key: API-SECRET


```python
from pyamplitude.amplituderestapi import AmplitudeRestApi
```

# Querying data from the Amplitude Analytics REST API Dashboard

Great ! So let's use the Amplitude Rest Api to query some useful data for later analysis...


```python
apiconector = AmplitudeRestApi(project_handler = bubbleConector,
                               show_logs       = False,
                               show_query_cost = False)
```

### Creating and using segments

Segments are represented as JSON arrays, where each element is a JSON object corresponding to a filter condition. First import and initialize the Segment class and add each query filter. in these cases we will be creating two segment definitions and for later use.

first_segment_definition = Segment()

first_segment_definition.add_filter(prop='country',op='is',values=['argentina','brasil'])

second_segment_definition = Segment()

second_segment_definition.add_filter(prop='country',op='is',values=['argentina','paraguay'])

### Using the AmplitudeRestApi module.

##### First Example:  Querying Active and New Users count


```python
data = apiconector.get_active_and_new_user_count(start    = '20170814',
                                                 end      = '20170825',
                                                 m        = 'active',
                                                 interval = 1,
                                                 segment_definitions = [first_segment_definition,
                                                                        second_segment_definition],
                                                 group_by            = None)
```
```python

If all goes well... you should receive a JSON response such as:

{
    "data": {
        "series": [
                    [18600,15294,14164,12945,12585,11797,10113,9523,8321,7873,9053,8109],
                    [3264,3423,3397,2984,2916,2827,2918,2934,1800,1560,1240,1100]
        ],
        "seriesMeta": ["Argentina", "Brasil"],
        "xValues": ["2017-08-14", "2017-08-15", "2017-08-16", "2017-08-17", "2017-08-18", "2017-08-19", "2017-08-20",
                    "2017-08-21", "2017-08-22", "2017-08-23", "2017-08-24", "2017-08-25"]
    }
}
```

Other Resources: Session Length Distribution, Average Session Length, Average Sessions per User, User Composition, Events, Events List, Event Segmentation, Funnel Analysis, Retention Analysis, User Activity, User Search, Real-time Active Users, Revenue Analysis, Revenue LTV, Annotations...

## Aditional options

#### Using  calculate_query_cost = True parameter

With PyAmplitude you can calculate each query cost very easily by checking the show_query_cost parameter. In an ETL context you may use this option not to exceed query limits. If you want to know more about how each query cost is being calculated, please read:

https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data#request-limits


# Fetching data from Amplitude Redshift

As a addition you can query data from Amplitude Redshift using the AmplitudeReshift module.


```python
from pyamplitude.amplituderestshift import AmplitudeRedshift
```


```python
ConnectionHandler = AmplitudeRedshift(host='',
                                      user='BubbleUser',
                                      port='5439',
                                      password=<yourpassword>,
                                      dbname='bubble_db',
                                      schema= 'app123098',
                                      table=<db_table>,
                                      show_logs= True)
```


```python
query = 'SELECT * FROM app123098.bubble_db LIMIT 10'
```


```python
ConnectionHandler.execute_query(query=query)
```

NOTE: AmplitudeRedshift has a serious of prebuild methods to fetch a list of users, query user events as well as new users, but you can also pass your specific query using the execute_query method.

## Authors

Marcos Manuel Muraro
