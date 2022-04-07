contains() {
    args=("$@")
    len=${#args[@]}

    ((len=len - 1))

    echo "l3n:$len"
    src_list=("${args[@]:0:$len}")
    last_element=${args[$len]}

    for element in "${src_list[@]}";
      do
          echo "element: $element"
          echo "last_element:$last_element"
          if [ "$element" = "$last_element" ]; then
          return 0
          fi
      done
    return 1
}