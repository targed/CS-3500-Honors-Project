# for each input file, test it with the python script and then compare the output using diff with the expected output
for i in {1..11}; do
    python3 main.py < sample_inputs/input$i.txt > actual_outputs/output$i.txt
    echo "Test $i:"
    diff -w actual_outputs/output$i.txt sample_outputs/output$i.txt && echo "PASSED" || echo "FAILED"
    echo ""
done