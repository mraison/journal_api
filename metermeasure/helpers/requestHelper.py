from .. import db
import click


def isUserAuthorizedForEndPoint(
        activeUser,      # by id
        targetUser,      # by id
        targetRecordSet, # by id
        action           # r, w, or rw
):
    # This function will check if <activeUser> is allowed to do <action> on
    # <targetUser>'s <targetRecordSet>

    # quick prevalidation step: construct sql searchable match for action.
    sqlSearchableAction = ''
    if action == 'r':
        sqlSearchableAction = 'r%'
    elif action == 'w':
        sqlSearchableAction = '%w'
    else:
        # This case should actually never get hit...we're only doing one action. you can't read AND write at the same time.
        sqlSearchableAction = ''.join(sorted(action))

    click.echo(
        "Validating access to: "+str(targetRecordSet)+
        "----owner:"+str(targetUser)+
        "----action:"+action+
        "requester:"+str(activeUser)
               )

    if (activeUser == targetUser): # check if user is owner
        click.echo('=>trigger 1')
        return True

    try:
        cursor = db.get_db().cursor()
        results = cursor.execute(
            'SELECT 1 as FOUND FROM recordSet rs '
            'INNER JOIN recordSetPermissionGroups rspg ON rs.recSetPermGroupName = rspg.name '
            'WHERE (rs.ID = ? ' # initial case: check if user is in the group defined on the record set.
            'AND   rs.userID = ? '
            'AND   rs.groupPermissions LIKE ? '
            'AND   rspg.userID = ?) '
            'OR    (rs.allPermissions LIKE ?) '
            'LIMIT 1', # check is record set allows anyone to do <action>
            (
                targetRecordSet,targetUser,sqlSearchableAction,activeUser,
                sqlSearchableAction
            )
        ).fetchall()

        db.get_db().commit()
        cursor.close()
    except Exception as e:
        # Hi there, Matt from the past here. we're going to need a logger here. @todo
        click.echo(str(e))
        return False

    if len(results) == 0:
        return False

    return True
