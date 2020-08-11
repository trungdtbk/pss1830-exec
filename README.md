# PSS1830-Executor

PSS-1830-Exec allows to run any command as CLI or as root in Nokia 1830 PSS nodes.

# Installation

## Install from source
  ```
  # git clone https://github.com/trungdtbk/pss1830-exec.git`
  # cd pss-1830-exec
  # python setup.py install
  # pssexec -v
  ```
  
# Usage Examples

## Gather General Information
`pssexec -m cli -u admin -p admin -c "show gen det" "show soft up sta"`

## Gather FHDM History
`pssexec -m root -u root -p root -c "/pureNeApp/EC/fmdh 1/1 history -a"`