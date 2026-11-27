# Create Assignment Type

> **Module:** `ssi_hr_manpower_planning_school`\
> **Model:** `manpower_planning_assignment_type`\
> **Menu:** Human Resource > Configuration > Manpower Planning > Assignment Types\
> **Actor:** user in group _Manpower Planning: Manpower Planning Assignment Type_

## Pre-Condition

- **Data:** The job position the type is usually given to exists (optional).
- **Access:** user in group _Manpower Planning: Manpower Planning Assignment Type_.

## Flow

1. Open the **Human Resource > Configuration > Manpower Planning > Assignment Types**
   menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the fields:
   - **Name** _(required)_: Enter the name of the assignment type.
   - **Code** _(required)_: Enter a unique code.
   - **Active**: Automatically checked.
4. Open the **Assignment** tab.
5. Fill in the assignment details:
   - **Category** _(required)_: Select the kind of assignment, for example Structural,
     Picket or Extracurricular Coach.
   - **Hour Basis** _(required)_: Select whether the hours are counted per week or per
     day. The default is Per Week.
   - **Default Hours**: Enter the hours copied to a new assignment line of this type.
   - **Job Position**: Select the job position this type is usually given to.
6. Click **Save**.

## Post-Condition

- A new assignment type is created and can be selected on the **Additional Assignments**
  tab of a manpower planning.
