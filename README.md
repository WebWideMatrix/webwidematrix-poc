Web-Wide-Matrix POC
===================

[![Join the chat at https://gitter.im/dibaunaumh/fcs-skateboard](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/dibaunaumh/fcs-skateboard?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

What is this
------------

This project is a reference implementation of a consumption layer over the Web,
transforming content feeds into organized spaces.
http://webwidematrix.org

It is based on several simple idioms:

1. It defines an environment which is recursively & infinitely
scalable, outward & inward.

In particular, this implementation uses the concept of a grid of buildings.
Each building can be an atomic container of JSON payload, or it can be
composed of floors. Each floor can also be a container of JSON payload, or
it can contain a grid of buildings. & so forth.

2. It allows streams of input & output to the real world.

In particular, this implementation has data-pipes that connect to a bldg floor
& either stream into it data items, that turn into buildings, arriving
from an external service, or stream out of it each new building, unto
an external service.

3. It contains also actors that move around inside the environment &
try to create value by processing data & creating new data. They aren't told
how to do anything, but instead try out things & learn by themselves based
on how much value they were able to create.

In particular, this implementation has residents moving inside the buildings,
that apply actions (external API's) on the JSON payload, to transform the
payload & create new buildings. The residents process the data arriving from
some input data-pipe, by applying on the JSON payloads API's available on the Internet,
that result in either more data inside the payload or new buildings, in the
same or different floor. The final buildings that result from their processing
are delivered to users via output data-pipe, & the users feedback on these results
is used to reinforce the residents learning, so that they improve in creating
value.

4. The process in which developers can affect the behavior of this system
is by providing knowledge or training environment that train the residents
in achieving some desired value creation. However, once the system is operational
the residents may alter their knowledge to adapt to changing user needs or data inputs.



We call the principles that this architecture is based on Life Oriented Programming,
although it's still unclear whether they'll prove useful or simple enough to implement.


To run:
-------

* **redis**: redis-server

* **meteor**: env REDIS_CONFIGURE_KEYSPACE_NOTIFICATIONS=1 meteor

* **workers**: celery -A mies worker -l info -B --concurrency=4 -Q default
* **residents**: celery -A mies worker -l info --concurrency=4 -Q life_events
* **actions**: celery -A mies worker -l info --concurrency=4 -Q actions
