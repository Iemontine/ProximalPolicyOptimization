# Proximal Policy Optimization (PPO)

    - rl algo using a on-policy method
    - on-policy method means the algo learns a policy to make decsions in the environment

# How it works at a high level

    - first collect trajectories
        - agent takes an action, environment returns a trajectory (state, action, reward, next_state)
    - next compute advantage estimates
        - advantage function computes how much better an action is compared to the average action at that state
        - PPO uses Genralized Advantage Estimation (GAE)
    - next update the policy
        - PPO uses a special objective function (to prevent the policy from updating too much in on episode, ensuring stability)
        - implemented by adding a penalty to the objective function if the new policy deviates too much from the original policy
    - iterate!

# Whats good about PPO

    - the objective function used for policy updates
    - uses a "clipped" verions of the policy ratio, adding a penalty if the new policy deviates too much
    - this ensures stability and effcient learning

# Actor-Critic

    - an actor controls how the agent behaves
    - a critic measures how good the action taken is

# Training Stability

    - use a ratio that indicates the difference between out current and old policy is not too big
    - clip this ration between [1 - epsilon, 1 + epsilon]

# The Inutuition

    - to limit policy changes, which imporoves training stability
    - in other words we want avoid having too large of a policy update
        - smaller updates are more likely to converge to an optimal solution
        - too big of a step can result in a long time of having no possibilty to recover
    - therefore we update policy conservatively
    - the clip ratio removes the incentive for the current policy to go too fart from the old one

# Clipped Surrogate Objective Function

    - the ratio function
    - r(theta) = probability(action | state) / probability_old(action | state)
        - r(theta) > 1, the action at that state is more likely in the current policy than the old one
        - r(theta) < 1, the action at that state is less likely in the current policy than the old one
    - A is the advantage
        - A > 0, this action is better than the other cation possible at that state
    - min(r(theta) * A) - the unclipped part
    - clip(r(theta), 1 - epsilon, 1 + epsilon) * A
        - PPO clip probability ratio in the objective function
    - min(r(theta) * A, clip(r(theta), 1 - epsilon, 1 + epsilon) * A)
    - we take the min of the unclipped and clipped objective function

    - So we update our policy only if:
    - Our ratio is in the range
        - [1−ϵ,1+ϵ]
    - Our ratio is outside the range, but the advantage leads to getting closer to the range
        - Being below the ratio but the advantage is > 0
        - Being above the ratio but the advantage is < 0
