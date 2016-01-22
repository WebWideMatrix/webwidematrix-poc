"""

Smell
- smell sources:
-- an hashset on Redis (key is bldg address, value is strength)
-- on bldg creation, create smell source with initial energy level, expiring in 1-24h TBD
-- on processing, update/remove smell source

- smell:
-- an hashset in Redis
-- updated on smell source changes
-- values expire after a day

- smell propagation:
-- define a foot print area around smell source
-- can be a circle of gradient decreasing strength
-- or rays of gradient decreasing strength
-- on smell source creation or strength increase: increase smell in footprint area
-- on smell source strength decrease: decrease smell in footprint area

- residents
-- create more than 1, per number of levels (at least until we have proper reproduction & navigation)
-- when moving, report their flr in Redis
-- if resident smells nothing, it will move to the user base flr, & start drilling into bldgs by their smell
-- on each flr arrived, if it has smell, it will check whether another resident is already there (using Redis hashset for residents current flr)
-- if so, it should climb to the flr above it

- resident flow:
-- smell around & move to bldg with strongest smell
-- if it has payload, process it

"""