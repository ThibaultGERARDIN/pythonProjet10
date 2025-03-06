from .models import Project, ProjectContributor


def check_contributors(project):
    """
    Return list of contributors to the project.
    """
    author = project.author
    contributors = ProjectContributor.objects.filter(project=project)
    contributors_list = []
    for contributor in contributors:
        contributors_list.append(contributor.user)
    if author not in contributors_list:
        contributors_list.append(author)

    return contributors_list


def get_viewable_projects(user):
    """
    Return list of projects the given user can view/access.
    """
    projects_list = []
    contributions = ProjectContributor.objects.filter(user=user)
    own_projects = Project.objects.filter(author=user)
    for project in own_projects:
        projects_list.append(project)

    for contribution in contributions:
        project = contribution.project
        if project not in projects_list:
            projects_list.append(project)

    return projects_list
