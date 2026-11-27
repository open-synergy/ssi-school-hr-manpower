# Create Recruitment Vacancy from Manpower Planning

> **Module:** `ssi_hr_manpower_planning_school_recruitment`\
> **Extends:** ssi_hr_manpower_planning_recruitment — model `manpower_planning`, aksi `16-create-recruitment-vacancy`

## Additional Pre-Condition

- **Module:** `ssi_hr_manpower_planning_school_recruitment` is installed.
- **Data:** The planning has a line on its **Teaching** tab without a teacher (vacant).
  Teaching lines that already have a recruitment vacancy of the planning, other than a
  cancelled one, are not proposed.
- **Config:** The job position of the teachers exists.

## Modified Flow

- Anchor: at base Flow step 4 (review **Date Start**), select the **Teacher Job
  Position** below **Date Start**. It is copied to the **Job Position** of every
  teaching line. Leave it empty when no teaching line is proposed.
- Anchor: at base Flow step 5 (review the proposed lines), one more line is proposed per
  vacant teaching line, after the lines of the job positions. A teaching line shows,
  besides the base columns:
  - **Subject**: The subject of the teaching line. Read-only.
  - **Weekly Hours**: The lesson hours per week of the teaching line, for all of its
    classes. It is proposed as the **Total Weekly Hours** of the teaching line.
  - **Total Classes**: The number of classes of the teaching line.
  - **Job Position**: Empty until **Teacher Job Position** is selected.
  - **Quantity** is proposed as 1. Enter the **Expected Join Date** as for any line.

## Modified Validation

- Creating the vacancies fails **if** a teaching line has no **Job Position**. Select
  the **Teacher Job Position** of the wizard.

## Additional Post-Condition

- The vacancy created for a teaching line carries its **Subject**, **Weekly Hours** and
  **Total Classes**, shown on the **Teaching** tab of the vacancy, and is linked to the
  teaching line.
- The teaching line is not proposed again by the wizard while its vacancy is not
  cancelled.
- The vacancies can be grouped by **Subject** in the vacancy list.
