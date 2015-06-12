"""

Smell
- smell sources:
-- an hashset on Redis (key is bldg address, value is strength)
-- on bldg creation, create smell source with initial energy level, expiring in 1-24h TBD
-- on processing, update/remove smell source

- smell:
-- an hashset in Redis
-- updated by smell propagator task
-- values expire after few minutes

- smell propagator:
-- periodic task
-- clears all smells
-- per each smell source:
--- increments the containing bldgs smell
--- draws rectangle around each smell source
--- per each bldg inside it, increments smell according to distance from source

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