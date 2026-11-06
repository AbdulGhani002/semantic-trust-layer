#!/usr/bin/env bash
# Runs every test that uses the language model, one after another, so timings stay clean.
# It takes about two and a half hours on the laptop. The traffic tests are separate.
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
rm -f logs/run_tests.done
export PYTHONIOENCODING=utf-8
run() {
  name=$1
  shift
  ./.venv/Scripts/python "$@" > "logs/$name.log" 2>&1
  echo "$name exit $?" | tee -a logs/run_tests.done.tmp
}
rm -f logs/run_tests.done.tmp
run compare_prompts training/compare_prompts.py BASE CALM GUARD FIRST --rules GUARD
run compare_link_rules training/compare_link_rules.py
run evaluate_text training/evaluate_text.py
run evaluate_links training/evaluate_links.py
run evaluate_review training/evaluate_review.py
run evaluate_system training/evaluate_system.py --per-group 150
run evaluate_system_fast training/evaluate_system.py --per-group 150 --no-language-model
mv logs/run_tests.done.tmp logs/run_tests.done
