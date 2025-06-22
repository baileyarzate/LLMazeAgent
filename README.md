## Overview

This repository contains a simple maze game implemented in Python used to compare maze-solving performance between human players and large language models (LLMs).

The goal is to log and analyze the time and number of moves it takes for humans and an LLM to solve randomized mazes over repeated trials.

The focal LLM will be Gemini 2.5 Flash due to low cost.

## Experimental Design

- **Human Trials:** Several human players will each play 30 randomized maze games. The number of moves and time taken to solve each maze will be recorded.  
  **Hypothesis 1:** Human players will improve over time, reducing both time and moves as they gain experience.

- **LLM Trials:** An LLM (using Google Gemini models) will also solve the same mazes, with the same metrics recorded. The LLM acts as an autonomous agent, not an algorithmic solver.  
  **Hypothesis 2:** The LLM will show no improvement in performance over time, maintaining relatively consistent time and moves.  
  **Hypothesis 3:** Higher performing LLMs will perform better on this task.

- **Comparison:**  
  **Hypothesis 4:** On average, the LLM will solve the maze faster and with fewer moves than humans but will not exhibit learning or improvement across trials.

## Status

This project is a work in progress.

## Usage

Run the maze game to start logging human or LLM gameplay data. Analysis scripts will be added to evaluate the collected metrics statistically.

## Attribution

The Pygame-based maze game implementation was adapted from the [Timed-Maze repository by DBgirl](https://github.com/DBgirl/PyGames/tree/c562037ec178991bb22b514c10d0fc0dfab38c13/Timed-Maze).

---

*Built using Python, Pygame, and Google Gemini LLM APIs.*
