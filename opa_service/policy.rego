package rig.policies

is_devops_team_member if {
    some t
    input.user.teams[t] == "devops"
}

deny contains reason if {
    input.user.login == "user-example"
    input.repo.name == "gitops"
    reason := "user-example cannot access repo gitops"
}

deny contains reason if {
    input.permission.level == "admin"
    not is_devops_team_member
    reason := sprintf("Admin access for user %s outside allowed team", [input.user.login])
}

deny contains reason if {
    input.user.mfa_enabled == false
    reason := sprintf("User %s has MFA disabled", [input.user.login])
}
