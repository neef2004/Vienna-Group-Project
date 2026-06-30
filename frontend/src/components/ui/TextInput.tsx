//reusable text input component with typescript prompts
import type React from "react";
//this section tells TypeScript what props the component accepts
type TextInputProps = {
  //? means label is optional
  label?: string;
  name: string;
  value: string;
  //event handler is the function that runs when the user types
  onChange: React.ChangeEventHandler<HTMLInputElement>;
  placeholder?: string;
  //only allows certain input types
  type?: "text" | "email" | "password" | "search" | "tel" | "url";
  required?: boolean;
  disabled?: boolean;
  error?: string;
};

//creates a component and pulls values ot of the props object
function TextInput({
  label,
  name,
  value,
  onChange,
  placeholder,
  type = "text",
  required = false,
  disabled = false,
  error,
}: TextInputProps) {
  //typescript annotation: says props must match TextInputPrompts
  return (
    <div className="text-input">
      {label && ( //only renders a label if 'label' exists
        //the label prompts the user what to type in the box
        <label className="text-input__label" htmlFor={name}>
          {label}
        </label>
      )}

      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        className={`text-input__field ${
          error ? "text-input__field--error" : ""
        }`}
      />

      {error && (
        <p className="text-input__error" id={`${name}-error`}>
          {error}
        </p>
      )}
    </div>
  );
}

export default TextInput;
