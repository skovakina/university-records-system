from django.db import models


class Department(models.Model):
	name = models.CharField(max_length=100, unique=True)
	faculty = models.CharField(max_length=100)

	class Meta:
		db_table = 'department'

	def __str__(self):
		return self.name


class Programme(models.Model):
	name = models.CharField(max_length=100, unique=True)
	degree_awarded = models.CharField(max_length=50)
	duration_years = models.PositiveSmallIntegerField()

	class Meta:
		db_table = 'programme'

	def __str__(self):
		return self.name


class Lecturer(models.Model):
	name = models.CharField(max_length=100)
	email = models.EmailField(unique=True)
	department = models.ForeignKey(Department, on_delete=models.PROTECT)
	committees = models.ManyToManyField(
		'Committee',
		through='LecturerCommittee',
		related_name='lecturers',
		blank=True,
	)

	class Meta:
		db_table = 'lecturer'

	def __str__(self):
		return self.name


class Student(models.Model):
	class GraduationStatus(models.TextChoices):
		ENROLLED = 'enrolled', 'Enrolled'
		GRADUATED = 'graduated', 'Graduated'
		WITHDRAWN = 'withdrawn', 'Withdrawn'

	name = models.CharField(max_length=100)
	birth_date = models.DateField()
	email = models.EmailField(unique=True)
	phone = models.CharField(max_length=20, blank=True, null=True)
	programme = models.ForeignKey(Programme, on_delete=models.PROTECT)
	year_of_study = models.PositiveSmallIntegerField()
	graduation_status = models.CharField(
		max_length=10,
		choices=GraduationStatus.choices,
		default=GraduationStatus.ENROLLED,
	)
	advisor = models.ForeignKey(Lecturer, on_delete=models.PROTECT)
	societies = models.ManyToManyField(
		'Society',
		through='StudentSociety',
		related_name='students',
		blank=True,
	)

	class Meta:
		db_table = 'student'

	def __str__(self):
		return self.name


class Staff(models.Model):
	class EmploymentType(models.TextChoices):
		FULL_TIME = 'full-time', 'Full-time'
		PART_TIME = 'part-time', 'Part-time'

	name = models.CharField(max_length=100)
	job_title = models.CharField(max_length=100)
	department = models.ForeignKey(Department, on_delete=models.PROTECT)
	employment_type = models.CharField(max_length=10, choices=EmploymentType.choices)
	contract_end_date = models.DateField(blank=True, null=True)
	salary = models.DecimalField(max_digits=10, decimal_places=2)
	emergency_contact_name = models.CharField(max_length=100, default='')
	emergency_contact_phone = models.CharField(max_length=20, default='')

	class Meta:
		db_table = 'staff'

	def __str__(self):
		return self.name


class Course(models.Model):
	course_code = models.CharField(max_length=10, unique=True)
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	department = models.ForeignKey(Department, on_delete=models.PROTECT)
	programmes = models.ManyToManyField(
		Programme,
		through='ProgrammeCourse',
		related_name='courses',
		blank=True,
	)
	lecturers = models.ManyToManyField(
		Lecturer,
		through='LecturerCourse',
		related_name='courses',
		blank=True,
	)
	prerequisites = models.ManyToManyField(
		'self',
		through='CoursePrerequisite',
		through_fields=('course', 'prerequisite'),
		symmetrical=False,
		blank=True,
	)
	level = models.PositiveSmallIntegerField()
	credits = models.PositiveSmallIntegerField()
	schedule = models.CharField(max_length=100, blank=True)

	class Meta:
		db_table = 'course'

	def __str__(self):
		return f'{self.course_code} - {self.name}'


class Society(models.Model):
	name = models.CharField(max_length=100, unique=True)

	class Meta:
		db_table = 'society'

	def __str__(self):
		return self.name


class Committee(models.Model):
	name = models.CharField(max_length=100, unique=True)

	class Meta:
		db_table = 'committee'

	def __str__(self):
		return self.name


class ResearchGroup(models.Model):
	name = models.CharField(max_length=100, unique=True)
	head_lecturer = models.OneToOneField(Lecturer, on_delete=models.PROTECT)

	class Meta:
		db_table = 'research_group'

	def __str__(self):
		return self.name


class Enrollment(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.PROTECT)
	grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

	class Meta:
		db_table = 'student_course'
		constraints = [
			models.UniqueConstraint(fields=['student', 'course'], name='unique_enrollment'),
			models.CheckConstraint(condition=models.Q(grade__gte=0) & models.Q(grade__lte=100), name='grade_range'),
		]

	def __str__(self):
		return f'{self.student} - {self.course.course_code}'


class LecturerCourse(models.Model):
	lecturer = models.ForeignKey(Lecturer, on_delete=models.PROTECT)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)

	class Meta:
		db_table = 'lecturer_course'
		constraints = [
			models.UniqueConstraint(
				fields=['lecturer', 'course'],
				name='unique_lecturer_course',
			),
		]

	def __str__(self):
		return f'{self.lecturer} - {self.course.course_code}'


class ProgrammeCourse(models.Model):
	programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.PROTECT)

	class Meta:
		db_table = 'programme_course'
		constraints = [
			models.UniqueConstraint(
				fields=['programme', 'course'],
				name='unique_programme_course',
			),
		]

	def __str__(self):
		return f'{self.programme} - {self.course.course_code}'


class CoursePrerequisite(models.Model):
	course = models.ForeignKey(
		Course,
		on_delete=models.CASCADE,
		related_name='prerequisite_links',
	)
	prerequisite = models.ForeignKey(
		Course,
		on_delete=models.PROTECT,
		related_name='required_by_links',
	)

	class Meta:
		db_table = 'course_prerequisite'
		constraints = [
			models.UniqueConstraint(
				fields=['course', 'prerequisite'],
				name='unique_course_prerequisite',
			),
		]

	def __str__(self):
		return f'{self.course.course_code} requires {self.prerequisite.course_code}'


class StudentSociety(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	society = models.ForeignKey(Society, on_delete=models.CASCADE)

	class Meta:
		db_table = 'student_society'
		constraints = [
			models.UniqueConstraint(
				fields=['student', 'society'],
				name='unique_student_society',
			),
		]

	def __str__(self):
		return f'{self.student} - {self.society}'


class LecturerCommittee(models.Model):
	lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
	committee = models.ForeignKey(Committee, on_delete=models.CASCADE)

	class Meta:
		db_table = 'lecturer_committee'
		constraints = [
			models.UniqueConstraint(
				fields=['lecturer', 'committee'],
				name='unique_lecturer_committee',
			),
		]

	def __str__(self):
		return f'{self.lecturer} - {self.committee}'


class ResearchProject(models.Model):
	title = models.CharField(max_length=200)
	lead_lecturer = models.ForeignKey(Lecturer, on_delete=models.PROTECT)
	research_group = models.ForeignKey(
		ResearchGroup,
		on_delete=models.PROTECT,
	)
	students = models.ManyToManyField(
		Student,
		through='ProjectStudent',
		related_name='research_projects',
		blank=True,
	)

	class Meta:
		db_table = 'project'

	def __str__(self):
		return self.title


class ProjectStudent(models.Model):
	project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)

	class Meta:
		db_table = 'project_student'
		constraints = [
			models.UniqueConstraint(
				fields=['project', 'student'],
				name='unique_project_student',
			),
		]

	def __str__(self):
		return f'{self.project} - {self.student}'


class Publication(models.Model):
	lecturer = models.ForeignKey(Lecturer, on_delete=models.PROTECT)
	project = models.ForeignKey(
		ResearchProject,
		on_delete=models.PROTECT,
		blank=True,
		null=True,
	)
	title = models.CharField(max_length=200)
	published_date = models.DateField()

	class Meta:
		db_table = 'publication'

	def __str__(self):
		return self.title


class LecturerQualification(models.Model):
	lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
	qualification = models.CharField(max_length=150)

	class Meta:
		db_table = 'lecturer_qualification'
		constraints = [
			models.UniqueConstraint(
				fields=['lecturer', 'qualification'],
				name='unique_lecturer_qualification',
			),
		]

	def __str__(self):
		return f'{self.lecturer} - {self.qualification}'


class LecturerExpertise(models.Model):
	lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
	expertise = models.CharField(max_length=100)

	class Meta:
		db_table = 'lecturer_expertise'
		constraints = [
			models.UniqueConstraint(
				fields=['lecturer', 'expertise'],
				name='unique_lecturer_expertise',
			),
		]

	def __str__(self):
		return f'{self.lecturer} - {self.expertise}'


class LecturerResearchInterest(models.Model):
	lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
	research_interest = models.CharField(max_length=100)

	class Meta:
		db_table = 'lecturer_research_interest'
		constraints = [
			models.UniqueConstraint(
				fields=['lecturer', 'research_interest'],
				name='unique_lecturer_research_interest',
			),
		]

	def __str__(self):
		return f'{self.lecturer} - {self.research_interest}'


class DepartmentResearchArea(models.Model):
	department = models.ForeignKey(Department, on_delete=models.CASCADE)
	research_area = models.CharField(max_length=100)

	class Meta:
		db_table = 'department_research_area'
		constraints = [
			models.UniqueConstraint(
				fields=['department', 'research_area'],
				name='unique_department_research_area',
			),
		]

	def __str__(self):
		return f'{self.department} - {self.research_area}'


class CourseMaterial(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	material = models.CharField(max_length=150)

	class Meta:
		db_table = 'course_material'
		constraints = [
			models.UniqueConstraint(
				fields=['course', 'material'],
				name='unique_course_material',
			),
		]

	def __str__(self):
		return f'{self.course} - {self.material}'


class ProjectFunding(models.Model):
	project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE)
	funding_source = models.CharField(max_length=100)

	class Meta:
		db_table = 'project_funding'
		constraints = [
			models.UniqueConstraint(
				fields=['project', 'funding_source'],
				name='unique_project_funding_source',
			),
		]

	def __str__(self):
		return f'{self.project} - {self.funding_source}'


class ProjectOutcome(models.Model):
	project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE)
	outcome = models.CharField(max_length=200)

	class Meta:
		db_table = 'project_outcome'
		constraints = [
			models.UniqueConstraint(
				fields=['project', 'outcome'],
				name='unique_project_outcome',
			),
		]

	def __str__(self):
		return f'{self.project} - {self.outcome}'


class DisciplinaryRecord(models.Model):
	student = models.ForeignKey(
		Student,
		on_delete=models.CASCADE,
		related_name='disciplinary_records',
	)
	incident_date = models.DateField()
	description = models.TextField()

	class Meta:
		db_table = 'student_disciplinary_record'

	def __str__(self):
		return f'{self.student} - {self.incident_date}'
