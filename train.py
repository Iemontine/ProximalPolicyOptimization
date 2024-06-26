from re import M
import torch
import numpy as np
import matplotlib.pyplot as plt

from stable_baselines3.common.vec_env import SubprocVecEnv, VecFrameStack, VecNormalize
from stable_baselines3.common.results_plotter import load_results, ts2xy, plot_results
from stable_baselines3.common.evaluation import evaluate_policy

from ppo import PPO
from helpers import Callback, make_env

# Define the parameters for the PPO model
params = {
	# Currently arbitrarily chosen values
	"gamma": 0.95,					# Discount factor
	"tau": 0.985,					# Factor for trade-off of bias vs variance in GAE
	"beta": 0.30,					# Entropy coefficient
	"epsilon": 0.75,				# Clipped surrogate objective
	"lr": 7.5e-4,					# Learning rate
	"steps": 512,					# Steps before updating policy, 4096 gives good results after 40mins training
	"batch_size": 8,				# Minibatch size
	"epochs": 10,					# Number of epoch when optimizing the surrogate loss
	# Development constants
	"total_timesteps": 1500000,
	"policy": "CnnPolicy",
	"num_envs": 5,
	"frame_skip": 8,
	"frame_stack": 8,
	"observation_dimension": (96, 96),
	"device": torch.device("cuda" if torch.cuda.is_available() else "cpu"),
	"render": True,
	"level": "1-1",
	"pass_num": 3,
}

def main():
	print(f"PyTorch Version: {torch.__version__}, CUDA Version: {torch.version.cuda}, CUDA Enabled: {torch.cuda.is_available()}")
	# losses = []

	env = SubprocVecEnv([make_env(params["level"], skip=params["frame_skip"], obs_dim=params["observation_dimension"], pass_num=params["pass_num"]) for _ in range(params["num_envs"])])
	env = VecFrameStack(env, n_stack=params["frame_stack"])

	# Create model
	model = PPO(
		gamma=params["gamma"],
		gae_lambda=params["tau"],
		ent_coef=params["beta"],
		clip_range=params["epsilon"],
		learning_rate=params["lr"],
		n_steps=params["steps"],
		batch_size=params["batch_size"],
		n_epochs=params["epochs"],
		env=env,
		policy=params["policy"],
		device=params["device"]
	)

	# Train model
	if params["pass_num"] == 1:
		# Pass 1: Discover the solution to the level
		model = PPO(params["policy"], env=env, verbose=1)
		model.learn(total_timesteps=params["total_timesteps"], progress_bar=True, callback=Callback(n_steps=params["steps"], verbose=1))
		model.save("sonic1")
		# Add an empty newline to levelbeats.csv
		with open('./logs/levelbeats.csv', 'a') as file: file.write('\n')
	elif params["pass_num"] == 2:
		# Pass 2: Refine the solution to the level, reward function tweaked to punish lack of progress, and reward speed
		model = PPO.load("sonic1", env=env, verbose=1)
		model.learn(total_timesteps=params["total_timesteps"], progress_bar=True, callback=Callback(n_steps=params["steps"], verbose=1))
		model.save("sonic2")
		with open('./logs/levelbeats.csv', 'a') as file: file.write('\n')
	elif params["pass_num"] == 3:
		# Pass 2: Refine the solution to the level, reward function tweaked to punish lack of progress, and reward speed
		# model = PPO.load("sonic2", env=env, verbose=1)
		model = PPO(params["policy"], env=env, verbose=1)
		model.learn(total_timesteps=params["total_timesteps"], progress_bar=True, callback=Callback(n_steps=params["steps"], verbose=1))
		model.save("sonic3")

if __name__ == "__main__":
	main()