from modules import jenkins as __jenkins
from modules import vicmachine as __vicmachine
from modules import scp as __scp
from modules import govc as __govc


MODULE = {
    "jenkins": __jenkins.MODULE,
    "vic": __vicmachine.MODULE,
    "scp": __scp.MODULE,
    "govc": __govc.MODULE,
}