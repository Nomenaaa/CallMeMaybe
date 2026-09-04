#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: nrasolom <nrasolom@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/03 10:47:00 by nrasolom            #+#    #+#            #
#   Updated: 2026/09/04 15:10:34 by nrasolom           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from main import main
from model_validations import PromptError, FunctionDefError, FunctionCallError
import sys


try:
    main()
except PromptError as e:
    print(e)
except FunctionDefError as e:
    print(e)
except FunctionCallError as e:
    print(e)
except KeyboardInterrupt:
    sys.exit(1)
