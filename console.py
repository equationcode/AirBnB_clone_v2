#!/usr/bin/python3
""" Console_Module """
import cmd
import sys
import re
import os
from datetime import datetime
import uuid
from models.base_model import BaseModel
from models import storage
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review


class HBNBCommand(cmd.Cmd):
    """ Contains_the functionality_for the_HBNB_console"""

    # determines_prompt for_interactive/non-interactive_modes
    prompt = '(hbnb) ' if sys.__stdin__.isatty() else ''

    classes = {
               'BaseModel': BaseModel, 'User': User, 'Place': Place,
               'State': State, 'City': City, 'Amenity': Amenity,
               'Review': Review
              }
    dot_cmds = ['all', 'count', 'show', 'destroy', 'update']
    types = {
             'number_rooms': int, 'number_bathrooms': int,
             'max_guest': int, 'price_by_night': int,
             'latitude': float, 'longitude': float
            }

    def preloop(self):
        """Prints_if isatty is_false"""
        if not sys.__stdin__.isatty():
            print('(hbnb)')

    def precmd(self, line):
        """Reformat_command line_for advanced command_syntax.

        Usage: <class_name>.<command>([<id> [<*args> or <**kwargs>]])
        (Brackets denote_optional_fields in usage example.)
        """
        _cmd = _cls = _id = _args = ''  # initialize_line_elements

        # scan_for_general_formating - i.e '.', '(', ')'
        if not ('.' in line and '(' in line and ')' in line):
            return line

        try:  # parse_line left_to_right
            pline = line[:]  # parsed_line

            # isolate_<class_name>
            _cls = pline[:pline.find('.')]

            # isolate_and_validate_<command>
            _cmd = pline[pline.find('.') + 1:pline.find('(')]
            if _cmd not in HBNBCommand.dot_cmds:
                raise Exception

            # if parantheses_contain_arguments,_parse them
            pline = pline[pline.find('(') + 1:pline.find(')')]
            if pline:
                # partition_args: (<id>, [<delim>], [<*args>])
                pline = pline.partition(', ')  # pline_convert to_tuple

                # isolate _id,_stripping_quotes
                _id = pline[0].replace('\"', '')
                # possible_bug_here:
                # empty_quotes register_as_empty _id when replaced

                # if_arguments_exist beyond_id
                pline = pline[2].strip()  # pline_is now_str
                if pline:
                    # check_for *args_or **kwargs
                    if pline[0] == '{' and pline[-1] == '}'\
                            and type(eval(pline)) is dict:
                        _args = pline
                    else:
                        _args = pline.replace(',', '')
                        # _args = _args.replace('\"', '')
            line = ' '.join([_cmd, _cls, _id, _args])

        except Exception as mess:
            pass
        finally:
            return line

    def postcmd(self, stop, line):
        """Prints_if isatty is_false"""
        if not sys.__stdin__.isatty():
            print('(hbnb) ', end='')
        return stop

    def do_quit(self, command):
        """ Method_to exit_the HBNB_console"""
        exit(0)

    def help_quit(self):
        """ Prints_the_help documentation_for quit  """
        print("Exits the program with formatting\n")

    def do_EOF(self, arg):
        """ Handles_EOF to exit_program """
        print()
        exit(0)

    def help_EOF(self):
        """ Prints_the help_documentation_for EOF """
        print("Exits the program without formatting\n")

    def emptyline(self):
        """ Overrides_the emptyline_method of_CMD """
        pass

    def do_create(self, args):
        """ Create_an object_of any_class"""
        ignored_attrs = ('id', 'created_at', 'updated_at', '__class__')
        class_name = ''
        name_pattern = r'(?P<name>(?:[a-zA-Z]|_)(?:[a-zA-Z]|\d|_)*)'
        class_match = re.match(name_pattern, args)
        obj_kwargs = {}
        if class_match is not None:
            class_name = class_match.group('name')
            params_str = args[len(class_name):].strip()
            params = params_str.split(' ')
            str_pattern = r'(?P<t_str>"([^"]|\")*")'
            float_pattern = r'(?P<t_float>[-+]?\d+\.\d+)'
            int_pattern = r'(?P<t_int>[-+]?\d+)'
            param_pattern = '{}=({}|{}|{})'.format(
                name_pattern,
                str_pattern,
                float_pattern,
                int_pattern
            )
            for param in params:
                param_match = re.fullmatch(param_pattern, param)
                if param_match is not None:
                    key_name = param_match.group('name')
                    str_v = param_match.group('t_str')
                    float_v = param_match.group('t_float')
                    int_v = param_match.group('t_int')
                    if float_v is not None:
                        obj_kwargs[key_name] = float(float_v)
                    if int_v is not None:
                        obj_kwargs[key_name] = int(int_v)
                    if str_v is not None:
                        obj_kwargs[key_name] = str_v[1:-1].replace('_', ' ')
        else:
            class_name = args
        if not class_name:
            print("** class name missing **")
            return
        elif class_name not in HBNBCommand.classes:
            print("** class doesn't exist **")
            return
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            if not hasattr(obj_kwargs, 'id'):
                obj_kwargs['id'] = str(uuid.uuid4())
            if not hasattr(obj_kwargs, 'created_at'):
                obj_kwargs['created_at'] = str(datetime.now())
            if not hasattr(obj_kwargs, 'updated_at'):
                obj_kwargs['updated_at'] = str(datetime.now())
            new_instance = HBNBCommand.classes[class_name](**obj_kwargs)
            new_instance.save()
            print(new_instance.id)
        else:
            new_instance = HBNBCommand.classes[class_name]()
            for key, value in obj_kwargs.items():
                if key not in ignored_attrs:
                    setattr(new_instance, key, value)
            new_instance.save()
            print(new_instance.id)

    def help_create(self):
        """ Help_information for_the create_method """
        print("Creates a class of any type")
        print("[Usage]: create <className>\n")

    def do_show(self, args):
        """ Method_to show_an individual_object """
        new = args.partition(" ")
        c_name = new[0]
        c_id = new[2]

        # guard_against_trailing args
        if c_id and ' ' in c_id:
            c_id = c_id.partition(' ')[0]

        if not c_name:
            print("** class name missing **")
            return

        if c_name not in HBNBCommand.classes:
            print("** class doesn't exist **")
            return

        if not c_id:
            print("** instance id missing **")
            return

        key = c_name + "." + c_id
        try:
            print(storage.all()[key])
        except KeyError:
            print("** no instance found **")

    def help_show(self):
        """ Help_information for_the show_command """
        print("Shows an individual instance of a class")
        print("[Usage]: show <className> <objectId>\n")

    def do_destroy(self, args):
        """ Destroys_a specified_object """
        new = args.partition(" ")
        c_name = new[0]
        c_id = new[2]
        if c_id and ' ' in c_id:
            c_id = c_id.partition(' ')[0]

        if not c_name:
            print("** class name missing **")
            return

        if c_name not in HBNBCommand.classes:
            print("** class doesn't exist **")
            return

        if not c_id:
            print("** instance id missing **")
            return

        key = c_name + "." + c_id

        try:
            storage.delete(storage.all()[key])
            storage.save()
        except KeyError:
            print("** no instance found **")

    def help_destroy(self):
        """ Help_information_for_the destroy_command """
        print("Destroys an individual instance of a class")
        print("[Usage]: destroy <className> <objectId>\n")

    def do_all(self, args):
        """ Shows all_objects, or_all objects_of a_class"""
        print_list = []

        if args:
            args = args.split(' ')[0]  # remove_possible trailing_args
            if args not in HBNBCommand.classes:
                print("** class doesn't exist **")
                return
            for k, v in storage.all().items():
                if k.split('.')[0] == args:
                    print_list.append(str(v))
        else:
            for k, v in storage.all().items():
                print_list.append(str(v))

        print(print_list)

    def help_all(self):
        """ Help_information for_the all_command """
        print("Shows all objects, or all of a class")
        print("[Usage]: all <className>\n")

    def do_count(self, args):
        """Count_current number_of class_instances"""
        count = 0
        for k, v in storage.all().items():
            if args == k.split('.')[0]:
                count += 1
        print(count)

    def help_count(self):
        """class of help count """
        print("Usage: count <class_name>")

    def do_update(self, args):
        """ Updates_a_certain_object with_new_info """
        c_name = c_id = att_name = att_val = kwargs = ''

        # isolate_cls from_id/args, ex: (<cls>, delim, <id/args>)
        args = args.partition(" ")
        if args[0]:
            c_name = args[0]
        else:  # class name_not_present
            print("** class name missing **")
            return
        if c_name not in HBNBCommand.classes:  # class_name_invalid
            print("** class doesn't exist **")
            return

        # isolate_id_from_args
        args = args[2].partition(" ")
        if args[0]:
            c_id = args[0]
        else:  # id_not present
            print("** instance id missing **")
            return

        # generate_key from_class and id
        key = c_name + "." + c_id

        # determine if_key is_present
        if key not in storage.all():
            print("** no instance found **")
            return

        # first_determine_if kwargs or args
        if '{' in args[2] and '}' in args[2] and type(eval(args[2])) is dict:
            kwargs = eval(args[2])
            args = []  # reformat_kwargs into_list, ex: [<name>, <value>, ...]
            for k, v in kwargs.items():
                args.append(k)
                args.append(v)
        else:  # isolate_args
            args = args[2]
            if args and args[0] == '\"':  # check_for quoted_arg
                second_quote = args.find('\"', 1)
                att_name = args[1:second_quote]
                args = args[second_quote + 1:]

            args = args.partition(' ')

            # if_att_name was not_quoted arg
            if not att_name and args[0] != ' ':
                att_name = args[0]
            # check_for quoted_val arg
            if args[2] and args[2][0] == '\"':
                att_val = args[2][1:args[2].find('\"', 1)]

            # if att_val was_not_quoted arg
            if not att_val and args[2]:
                att_val = args[2].partition(' ')[0]

            args = [att_name, att_val]

        # retrieve_dictionary_of current_objects
        new_dict = storage.all()[key]

        # iterate_through attr_names and_values
        for i, att_name in enumerate(args):
            # block_only runs on even_iterations
            if (i % 2 == 0):
                att_val = args[i + 1]  # following_item is_value
                if not att_name:  # check_for att_name
                    print("** attribute name missing **")
                    return
                if not att_val:  # check_for att_value
                    print("** value missing **")
                    return
                # type_cast as_necessary
                if att_name in HBNBCommand.types:
                    att_val = HBNBCommand.types[att_name](att_val)

                # update_dictionary with_name, value_pair
                new_dict.__dict__.update({att_name: att_val})

        new_dict.save()  # save_updates to_file

    def help_update(self):
        """ Help_information_for the update_class """
        print("Updates an object with new information")
        print("Usage: update <className> <id> <attName> <attVal>\n")


if __name__ == "__main__":
    HBNBCommand().cmdloop()
