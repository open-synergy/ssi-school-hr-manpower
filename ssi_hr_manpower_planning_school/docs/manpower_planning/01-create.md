# Create Manpower Planning

> **Module:** `ssi_hr_manpower_planning_school`\
> **Extends:** ssi_hr_manpower_planning — model `manpower_planning`, aksi `01-create`

## Additional Pre-Condition

- **Module:** `ssi_hr_manpower_planning_school` is installed.
- **Data:** The school and academic year the planning is made for exist (optional).
- **Data:** The school has a school curriculum that is **On Progress** (optional). It is
  filled in the **Curriculum** field when the school is selected.
- **Data:** The subjects with their applicable grades, the grades, the classes of the
  school and the teachers exist (needed for the **Teaching** tab).
- **Data:** The assignment types exist (needed for the **Additional Assignments** tab).

## Additional Fields

When this module is installed, the planning form gains four tabs after **Summary**. All
of the new fields are optional, so a planning without school data is still valid.

On the **School** tab:

- **School**: Select the school unit the planning is made for.
- **School Branch**: Automatically filled from **School**. Read-only.
- **Academic Year**: Select the academic year. **Date Start** and **Date End** in the
  header are automatically filled from the academic year. Change if needed.
- **Curriculum**: Automatically filled with the school curriculum that is **On
  Progress** for the selected **School**, and left empty when the school has none.
  Change or empty it if needed; only the **On Progress** curriculums of the school are
  listed. Leave it empty for a planning that does not follow a curriculum, for example a
  planning of non-teacher staff.

On the **Teaching** tab, click **Add a line**. Repeat the following steps as many times
as needed:

- **Subject** _(required)_: Select the subject taught. It must be applicable to the
  selected grade.
- **Grade** _(required)_: Select the grade the subject is taught on.
- **Classes**: Select the classes of the grade that are taught. Only the classes of the
  selected **School** are listed. A class can be used by only one line of the same
  subject.
- **Weekly Hours per Class** _(required)_: Enter the lesson hours per week in each
  class. It must be at least 1.
- **Total Classes**: Automatically counted from **Classes**. Read-only.
- **Total Weekly Hours**: Automatically calculated as **Weekly Hours per Class** times
  **Total Classes**. Read-only.
- **Teacher**: Select the employee who teaches. Leave empty when the line is vacant.
- **Co-Teacher**: Select the employee who assists the teacher. It must be a different
  employee than the teacher.
- **Teaching Assignment Lines**: Shown as tags at the end of the line. Filled when the
  line is imported from a teaching assignment (see the Import Teaching Lines from
  Teaching Assignment work instruction); leave it empty for a manual line. A line can
  also be generated from the curriculum (see the Generate Teaching Lines from Curriculum
  work instruction).

On the **Additional Assignments** tab, click **Add a line**. Repeat the following steps
as many times as needed:

- **Assignment Type** _(required)_: Select the assignment type.
- **Category**: Automatically filled from **Assignment Type**. Read-only.
- **Hour Basis**: Automatically filled from **Assignment Type**. Read-only.
- **Employee**: Select the employee who holds the assignment. Leave empty when the line
  is vacant.
- **Position**: Select Coach or Assistant Coach. Shown only for the achievement coaching
  and extracurricular categories.
- **Hours**: Automatically filled from the default hours of **Assignment Type**. Change
  if needed.
- **Number of Classes**: Enter the number of classes handled. Shown only for the
  achievement coaching and extracurricular categories.

## Modified Validation

- Saving a **Teaching** line fails **if** the subject is not applicable to the grade,
  the weekly hours per class are lower than 1, the co-teacher is the same employee as
  the teacher, or a class is already used by another line of the same subject in the
  planning.

## Additional Post-Condition

- The **Workload** tab lists, per employee, the teaching hours, the number of
  co-teaching lines, the additional assignment hours per week and per day, and the total
  weekly hours. It is read-only and is recalculated from the lines. Lines without an
  employee are left out.
