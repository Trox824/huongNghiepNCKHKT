# RIASEC Score Calculation Method

## Overview

The RIASEC scoring system uses a **weighted average** approach based on student responses to assessment questions. Each question belongs to one of the six RIASEC categories (R, I, A, S, E, C) and has a weight indicating its importance.

## Step-by-Step Calculation

### Step 1: Answer Evaluation

Each question is evaluated independently by an AI model, which returns one of three answers:

- **"Yes"** = Strong evidence supporting the trait → **Score: 1.0**
- **"Partial"** = Some evidence but not conclusive → **Score: 0.5**
- **"No"** = Little or no evidence → **Score: 0.0**

### Step 2: Weighted Score Accumulation

For each RIASEC category, the system:

1. **Initializes** scores and weights to 0 for each category (R, I, A, S, E, C)
2. **Iterates** through all assessment responses
3. **For each response:**
   - Finds the corresponding question in the framework
   - Gets the question's `riasec_code` (R, I, A, S, E, or C)
   - Gets the question's `weight` (from CSV, typically 0.6 to 1.0)
   - Calculates contribution: `score × weight`
   - Adds to the category's total score: `riasec_scores[code] += score × weight`
   - Adds to the category's total weight: `riasec_weights[code] += weight`

### Step 3: Normalization

After processing all responses, scores are normalized to a 0-100 scale:

```python
for code in riasec_scores.keys():
    if riasec_weights[code] > 0:
        riasec_scores[code] = (riasec_scores[code] / riasec_weights[code]) × 100
```

This gives a **percentage score** where:

- **100** = All questions answered "Yes" (perfect match)
- **50** = All questions answered "Partial" (moderate match)
- **0** = All questions answered "No" (no match)

## Example Calculation

### Example: C (Conventional) Category

**Framework Questions for C:**

- Q66: Weight 0.9
- Q67: Weight 0.9
- Q68: Weight 0.8
- Q69: Weight 0.9
- Q70: Weight 0.8
- Q71: Weight 0.7
- Q72: Weight 0.9

**Total Weight:** 0.9 + 0.9 + 0.8 + 0.9 + 0.8 + 0.7 + 0.9 = **5.9**

**Student Responses:**

- Q66: Yes (1.0) → Contribution: 1.0 × 0.9 = 0.9
- Q67: Yes (1.0) → Contribution: 1.0 × 0.9 = 0.9
- Q68: Yes (1.0) → Contribution: 1.0 × 0.8 = 0.8
- Q69: Yes (1.0) → Contribution: 1.0 × 0.9 = 0.9
- Q70: Yes (1.0) → Contribution: 1.0 × 0.8 = 0.8
- Q71: Yes (1.0) → Contribution: 1.0 × 0.7 = 0.7
- Q72: Yes (1.0) → Contribution: 1.0 × 0.9 = 0.9

**Total Score:** 0.9 + 0.9 + 0.8 + 0.9 + 0.8 + 0.7 + 0.9 = **5.9**

**Normalized Score:** (5.9 / 5.9) × 100 = **100.00**

### Example with Mixed Answers

**Student Responses:**

- Q66: Yes (1.0) → 1.0 × 0.9 = 0.9
- Q67: Partial (0.5) → 0.5 × 0.9 = 0.45
- Q68: Yes (1.0) → 1.0 × 0.8 = 0.8
- Q69: Partial (0.5) → 0.5 × 0.9 = 0.45
- Q70: Yes (1.0) → 1.0 × 0.8 = 0.8
- Q71: No (0.0) → 0.0 × 0.7 = 0.0
- Q72: Yes (1.0) → 1.0 × 0.9 = 0.9

**Total Score:** 0.9 + 0.45 + 0.8 + 0.45 + 0.8 + 0.0 + 0.9 = **4.3**

**Normalized Score:** (4.3 / 5.9) × 100 = **72.88**

## Code Implementation

```python
def calculate_riasec_scores(self, assessment_responses: List[Dict], framework_df: pd.DataFrame) -> Dict[str, float]:
    # Initialize scores
    riasec_scores = {'R': 0.0, 'I': 0.0, 'A': 0.0, 'S': 0.0, 'E': 0.0, 'C': 0.0}
    riasec_weights = {code: 0.0 for code in riasec_scores.keys()}

    # Calculate weighted scores
    for response in assessment_responses:
        # Find corresponding question
        question = framework_df[framework_df['id'] == response['question_id']].iloc[0]
        riasec_code = question['riasec_code']
        weight = float(question['weight'])

        # Calculate score contribution
        if response['answer'] == 'Yes':
            score = 1.0
        elif response['answer'] == 'Partial':
            score = 0.5
        else:  # No or Error
            score = 0.0

        riasec_scores[riasec_code] += score * weight
        riasec_weights[riasec_code] += weight

    # Normalize scores
    for code in riasec_scores.keys():
        if riasec_weights[code] > 0:
            riasec_scores[code] = (riasec_scores[code] / riasec_weights[code]) * 100

    return riasec_scores
```

## Key Features

1. **Weighted System**: Not all questions are equal - important questions have higher weights
2. **Normalized to 0-100**: Makes scores comparable across categories
3. **Handles Missing Data**: If a category has no questions, score remains 0.0
4. **Proportional Scoring**: Partial answers contribute 50% of full credit

## Why This Method?

1. **Flexibility**: Different questions can have different importance (weights)
2. **Fairness**: Normalization ensures categories with different numbers of questions are comparable
3. **Granularity**: Three-level answers (Yes/Partial/No) provide more nuance than binary
4. **Transparency**: Easy to understand and verify calculations

## Current Issue

The current implementation correctly calculates scores, but the **evaluation step** (Step 1) may be too lenient, causing many students to get "Yes" for all questions in certain categories (like C), resulting in identical scores of 100.00.

The improved evaluation logic now:

- Includes framework metadata (key subjects, required grades)
- Requires stronger evidence for "Yes" answers
- Is more discriminating, especially for C questions
- Considers trends and consistency, not just absolute scores
